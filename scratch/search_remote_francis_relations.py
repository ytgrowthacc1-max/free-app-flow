import subprocess

queries = {
    "DailyCheckin": "SELECT count(*) FROM DailyCheckin WHERE customerId = '0ebb68c1-9af5-4560-8aba-593e4b793afe';",
    "WeightLog": "SELECT count(*) FROM WeightLog WHERE customerId = '0ebb68c1-9af5-4560-8aba-593e4b793afe';",
    "TrainingAssignment": "SELECT count(*), trainingProgramId FROM TrainingAssignment WHERE customerId = '0ebb68c1-9af5-4560-8aba-593e4b793afe';",
    "CoachCustomerAssignment": "SELECT count(*) FROM CoachCustomerAssignment WHERE customerId = '0ebb68c1-9af5-4560-8aba-593e4b793afe';",
}

output = []
for name, q in queries.items():
    cmd = ["npx", "wrangler", "d1", "execute", "DB", "--remote", f"--command={q}", "--config=../Health_APP_WHOP/wrangler.toml"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    output.append(f"Remote {name}:")
    output.append(res.stdout)

with open("scratch/remote_francis_relations_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
