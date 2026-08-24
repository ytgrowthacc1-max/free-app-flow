import subprocess
import json
import sys

def run_d1(sql):
    cmd = f'npx wrangler d1 execute DB --remote --command="{sql}" --config=../Health_APP_WHOP/wrangler.toml --json'
    res = subprocess.run(cmd, capture_output=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True)
    out = res.stdout.decode("utf-8", errors="replace")
    err = res.stderr.decode("utf-8", errors="replace")
    if res.returncode != 0:
        print("ERROR:", err[:500])
        return []
    try:
        data = json.loads(out)
        return data[0].get("results", []) if data else []
    except Exception as e:
        print("JSON parse error:", e, "| output:", out[:300])
        return []

print("=== D1 Row Counts ===")
rows = run_d1("SELECT COUNT(*) as cnt FROM User")
print("Users:", rows[0].get("cnt") if rows else "ERR")
rows = run_d1("SELECT COUNT(*) as cnt FROM Exercise")
print("Exercises:", rows[0].get("cnt") if rows else "ERR")
rows = run_d1("SELECT COUNT(*) as cnt FROM TrainingProgram")
print("Programs:", rows[0].get("cnt") if rows else "ERR")
rows = run_d1("SELECT COUNT(*) as cnt FROM CoachCustomerAssignment")
print("CoachCustomerAssignments:", rows[0].get("cnt") if rows else "ERR")
rows = run_d1("SELECT COUNT(*) as cnt FROM DailyCheckin")
print("DailyCheckins:", rows[0].get("cnt") if rows else "ERR")
rows = run_d1("SELECT COUNT(*) as cnt FROM TrainingAssignment")
print("TrainingAssignments:", rows[0].get("cnt") if rows else "ERR")

print()
print("=== User Sample ===")
users = run_d1("SELECT id, whopUserId, email, role FROM User LIMIT 8")
for u in users:
    print(f"  id={u.get('id','?')[:20]}  whopUserId={u.get('whopUserId','?')}  role={u.get('role','?')}  email={u.get('email','?')}")

print()
print("=== Check DailyCheckin / WeightLog tables exist ===")
tables = run_d1("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("Tables:", [t.get("name") for t in tables])
