import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = "npx wrangler d1 execute 6839fec9-ebad-41e9-829f-f618f21ce184 --remote --command=\"SELECT name, sql FROM sqlite_schema WHERE type='table' AND name IN ('Exercise', 'NutritionPlan', 'TrainingAssignment', 'NutritionAssignment', 'SupplementPlan', 'SupplementAssignment', 'DailyCheckin', 'WeightLog');\" --json"
res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True)
if res.returncode != 0:
    print("Error querying schema:", res.stderr)
    sys.exit(1)

tables = json.loads(res.stdout)[0].get("results", [])
for t in tables:
    print(f"--- TABLE: {t['name']} ---")
    print(t['sql'])
    print()
