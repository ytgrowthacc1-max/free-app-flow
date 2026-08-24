import subprocess
import json

tables = [
    'CoachCustomerAssignment', 'TrainingProgram', 'Workout', 'Exercise',
    'NutritionPlan', 'Meal', 'TrainingAssignment', 'NutritionAssignment',
    'Supplement', 'SupplementPlan', 'SupplementPlanItem', 'SupplementAssignment',
    'DailyCheckin', 'WeightLog', 'User', 'WorkoutExercise'
]

def run_query(cmd):
    full_cmd = [
        "npx", "wrangler", "d1", "execute", "DB", "--remote",
        "--config=../Health_APP_WHOP/wrangler.toml",
        f"--command={cmd}"
    ]
    res = subprocess.run(full_cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"Error for query {cmd}: {res.stderr}")
        return None
    try:
        # Find start of JSON
        out = res.stdout
        idx = out.find("[")
        if idx != -1:
            data = json.loads(out[idx:])
            return data[0]["results"]
    except Exception as e:
        print("Failed to parse:", e)
        print("Output was:", res.stdout)
    return None

def main():
    print("Fetching remote counts...")
    for t in tables:
        res = run_query(f"SELECT COUNT(*) as count FROM \"{t}\";")
        if res:
            print(f"{t}: {res[0]['count']}")
        else:
            print(f"{t}: Error or no data")

if __name__ == "__main__":
    main()
