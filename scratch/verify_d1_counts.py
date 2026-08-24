import subprocess
import json

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

expected = {
    "User": 151,
    "CoachCustomerAssignment": 117,
    "TrainingProgram": 181,
    "Workout": 6110,
    "WorkoutExercise": 32476
}

print("Checking remote D1 database counts:")
all_passed = True
for table, exp_count in expected.items():
    res = query_remote(f"SELECT COUNT(*) as count FROM \"{table}\";")
    count = res[0]["count"] if res else 0
    passed = (count == exp_count)
    if not passed:
        all_passed = False
    print(f"  Table '{table}': Actual count = {count}, Expected count = {exp_count} -> {'PASSED' if passed else 'FAILED'}")

if all_passed:
    print("\nALL COUNTS MATCH PERFECTLY! Database integrity is verified.")
else:
    print("\nWARNING: Some counts do not match!")
