import sqlite3
import subprocess
import json

LOCAL_DB = "c:/Python/Health_APP_WHOP/prisma/dev.db"
WRANGLER_CONFIG = "../Health_APP_WHOP/wrangler.toml"

def query_remote(sql):
    cmd = [
        "npx", "wrangler", "d1", "execute", "DB", 
        "--remote", f"--command={sql}", 
        f"--config={WRANGLER_CONFIG}", "--json"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    if res.returncode != 0:
        raise Exception(f"Query failed: {res.stderr}\nCommand: {sql}")
    try:
        data = json.loads(res.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("results", [])
        return []
    except Exception as e:
        raise Exception(f"JSON parse failed: {e}\nOutput: {res.stdout}")

# 1. Get local tables and schemas
local_conn = sqlite3.connect(LOCAL_DB)
local_cursor = local_conn.cursor()
local_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
local_tables = [t[0] for t in local_cursor.fetchall() if not t[0].startswith("_") and t[0] != "sqlite_sequence"]

local_schemas = {}
for table in local_tables:
    local_cursor.execute(f"PRAGMA table_info({table});")
    cols = {r[1]: (r[2], r[3], r[4], r[5]) for r in local_cursor.fetchall()}
    local_schemas[table] = cols
local_conn.close()

# 2. Get remote schemas
print("Comparing local and remote database schemas:")
for table in sorted(local_tables):
    print(f"Checking table '{table}'...")
    try:
        remote_cols = query_remote(f"PRAGMA table_info(\"{table}\");")
        remote_schema = {r["name"]: (r["type"], r["notnull"], r["dflt_value"], r["pk"]) for r in remote_cols}
    except Exception as e:
        print(f"Error fetching remote schema for table {table}: {e}")
        continue
        
    local_schema = local_schemas[table]
    
    # Check for missing columns in remote
    missing_in_remote = [c for c in local_schema if c not in remote_schema]
    if missing_in_remote:
        print(f"  [MISMATCH] Table '{table}': Columns missing in remote D1: {missing_in_remote}")
        
    # Check for missing columns in local
    missing_in_local = [c for c in remote_schema if c not in local_schema]
    if missing_in_local:
        print(f"  [MISMATCH] Table '{table}': Columns extra in remote D1: {missing_in_local}")
        
    # Check for type/nullability mismatches
    mismatches = 0
    for col in sorted(set(local_schema.keys()) & set(remote_schema.keys())):
        l_type, l_notnull, l_dflt, l_pk = local_schema[col]
        r_type, r_notnull, r_dflt, r_pk = remote_schema[col]
        
        # Normalize types
        def norm_type(t):
            t = t.upper()
            if t in ["TEXT", "VARCHAR", "STRING"]:
                return "TEXT"
            if t in ["INT", "INTEGER"]:
                return "INTEGER"
            if t in ["FLOAT", "REAL", "DOUBLE"]:
                return "REAL"
            if t in ["BOOLEAN", "BOOL"]:
                return "BOOLEAN"
            return t
            
        if norm_type(l_type) != norm_type(r_type) or l_notnull != r_notnull or l_pk != r_pk:
            print(f"  [MISMATCH] Table '{table}', Column '{col}':")
            print(f"    Local:  type={l_type}, notnull={l_notnull}, pk={l_pk}")
            print(f"    Remote: type={r_type}, notnull={r_notnull}, pk={r_pk}")
            mismatches += 1

    if not missing_in_remote and not missing_in_local and mismatches == 0:
        print(f"  Table '{table}' schema matched perfectly!")

print("Schema comparison completed.")
