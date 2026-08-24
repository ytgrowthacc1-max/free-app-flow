import sqlite3
import subprocess
import json

output = []

# Local Search
output.append("--- LOCAL PROGRAMS ---")
try:
    conn = sqlite3.connect("c:/Python/Health_APP_WHOP/prisma/dev.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, ownerId FROM TrainingProgram WHERE name LIKE '%Francis%' OR name LIKE '%francis%';")
    for r in cursor.fetchall():
        output.append(f"Local: ID={r[0]}, Name={r[1]}, Owner={r[2]}")
    conn.close()
except Exception as e:
    output.append(f"Local error: {e}")

# Remote Search
output.append("\n--- REMOTE D1 PROGRAMS ---")
cmd = ["npx", "wrangler", "d1", "execute", "DB", "--remote", "--command=SELECT id, name, ownerId FROM TrainingProgram WHERE name LIKE '%Francis%' OR name LIKE '%francis%';", "--config=../Health_APP_WHOP/wrangler.toml"]
res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
output.append(res.stdout)

with open("scratch/search_francis_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
