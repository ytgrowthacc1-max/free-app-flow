import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

tables = [
    "User", "CoachCustomerAssignment", "TrainingProgram", "Workout", "Exercise",
    "WorkoutExercise", "NutritionPlan", "Meal", "TrainingAssignment", "NutritionAssignment",
    "Supplement", "SupplementPlan", "SupplementPlanItem", "SupplementAssignment",
    "DailyCheckin", "WeightLog"
]

print("Verifying tables are readable:")
for t in tables:
    cmd = f"npx wrangler d1 execute 6839fec9-ebad-41e9-829f-f618f21ce184 --remote --command=\"SELECT COUNT(*) FROM \\\"{t}\\\";\" --json"
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True)
    if res.returncode != 0:
        print(f"  [ERROR] {t}: {res.stderr.strip()}")
    else:
        try:
            count = json.loads(res.stdout)[0].get("results", [])[0].get("COUNT(*)")
            print(f"  [OK] {t}: {count} rows")
        except Exception as e:
            print(f"  [ERROR] Parsing {t}: {e}")
