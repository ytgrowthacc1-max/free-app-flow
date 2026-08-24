import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

CWD = r"c:\Python\WHOP AUTOMATION AGENTIC"
CONFIG = "../Health_APP_WHOP/wrangler.toml"

def run_d1_cmd(sql, label=""):
    cmd = f'npx wrangler d1 execute DB --remote --command="{sql}" --config={CONFIG} --json'
    res = subprocess.run(cmd, capture_output=True, cwd=CWD, shell=True)
    out = res.stdout.decode("utf-8", errors="replace")
    err = res.stderr.decode("utf-8", errors="replace")
    if res.returncode != 0:
        print(f"  ERROR {label}: {err[:300]}")
        return None
    try:
        data = json.loads(out)
        return data[0].get("results", [])
    except:
        print(f"  JSON parse error for {label}: {out[:200]}")
        return None

def run_d1_file(path, label=""):
    cmd = f'npx wrangler d1 execute DB --remote --file="{path}" --config={CONFIG}'
    res = subprocess.run(cmd, capture_output=True, cwd=CWD, shell=True)
    out = res.stdout.decode("utf-8", errors="replace")
    err = res.stderr.decode("utf-8", errors="replace")
    if res.returncode != 0:
        print(f"  ERROR {label}: {err[:500]}")
        return False
    print(f"  OK {label}")
    return True

# Tables with datetime columns to fix
TABLES_WITH_DATETIMES = [
    ("User",                   ["createdAt", "updatedAt"]),
    ("TrainingProgram",        ["createdAt", "updatedAt"]),
    ("Workout",                ["createdAt", "updatedAt"]),
    ("Exercise",               ["createdAt", "updatedAt"]),
    ("NutritionPlan",          ["createdAt", "updatedAt"]),
    ("Meal",                   ["createdAt", "updatedAt"]),
    ("SupplementPlan",         ["createdAt", "updatedAt"]),
    ("Supplement",             ["createdAt", "updatedAt"]),
    ("CoachCustomerAssignment",["createdAt"]),
    ("TrainingAssignment",     ["createdAt", "startDate", "endDate"]),
    ("NutritionAssignment",    ["createdAt", "startDate", "endDate"]),
    ("SupplementAssignment",   ["createdAt", "startDate", "endDate"]),
    ("DailyCheckin",           ["createdAt", "updatedAt"]),
    ("WeightLog",              ["createdAt", "updatedAt"]),
]

print("Checking datetime formats...")
needs_fix = []
for table, cols in TABLES_WITH_DATETIMES:
    col = cols[0]
    rows = run_d1_cmd(f"SELECT {col} FROM \"{table}\" LIMIT 1", table)
    if rows and rows[0].get(col):
        val = str(rows[0][col])
        if "+00:00" in val or (val and "Z" not in val and "T" in val):
            print(f"  NEEDS FIX: {table}.{col} = {val}")
            needs_fix.append((table, cols))
        else:
            print(f"  OK: {table}.{col} = {val}")

if not needs_fix:
    print("\nAll datetime columns look correct! No fix needed.")
    sys.exit(0)

print(f"\nFixing {len(needs_fix)} tables...")

# Build SQL update statements
sql_parts = ["PRAGMA foreign_keys = OFF;"]
for table, cols in needs_fix:
    for col in cols:
        # Replace +00:00 with Z, and fix any space-separated datetimes
        sql_parts.append(
            f"UPDATE \"{table}\" SET \"{col}\" = REPLACE(REPLACE(\"{col}\", '+00:00', 'Z'), ' ', 'T') "
            f"WHERE \"{col}\" LIKE '%+00:00' OR (\"{col}\" LIKE '% %' AND \"{col}\" NOT LIKE '%Z');"
        )

sql_parts.append("PRAGMA foreign_keys = ON;")
fix_sql = "\n".join(sql_parts)

sql_file = "scratch/fix_datetimes.sql"
with open(sql_file, "w", encoding="utf-8") as f:
    f.write(fix_sql)

print(f"Running fix SQL ({len(sql_parts)} statements)...")
ok = run_d1_file(sql_file, "datetime fix")

if ok:
    print("\nVerifying fix...")
    for table, cols in needs_fix:
        col = cols[0]
        rows = run_d1_cmd(f"SELECT {col} FROM \"{table}\" LIMIT 1", table)
        if rows:
            val = str(rows[0].get(col, ""))
            status = "OK" if val.endswith("Z") or not val else "STILL WRONG"
            print(f"  {status}: {table}.{col} = {val}")
    print("\nDone!")
