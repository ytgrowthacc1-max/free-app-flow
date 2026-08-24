import subprocess
import json

tables = [
    "CoachCustomerAssignment",
    "TrainingProgram",
    "Workout",
    "Exercise",
    "NutritionPlan",
    "Meal",
    "TrainingAssignment",
    "NutritionAssignment",
    "Supplement",
    "SupplementPlan",
    "SupplementPlanItem",
    "SupplementAssignment",
    "DailyCheckin",
    "WeightLog",
    "User",
    "WorkoutExercise"
]

output = []
for table in tables:
    cmd = ["npx", "wrangler", "d1", "execute", "DB", "--remote", f"--command=SELECT count(*) FROM {table};", "--config=../Health_APP_WHOP/wrangler.toml"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    output.append(f"Table: {table}")
    output.append(res.stdout)

with open("scratch/remote_db_stats_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
