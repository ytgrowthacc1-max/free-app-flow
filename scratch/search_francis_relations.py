import subprocess
import json

queries = [
    # Workouts for Francis programs
    "SELECT id, trainingProgramId, title FROM Workout WHERE trainingProgramId IN ('91f4d177-440f-4a2a-9211-20cb46c7e31b', '8a5336b6-ae24-48fe-a94d-fa7a2d9f21f2', 'dbd17282-36e0-4f2a-8124-cd7517e97083');",
    # Training assignments for Francis programs
    "SELECT id, customerId, coachId, trainingProgramId FROM TrainingAssignment WHERE trainingProgramId IN ('91f4d177-440f-4a2a-9211-20cb46c7e31b', '8a5336b6-ae24-48fe-a94d-fa7a2d9f21f2', 'dbd17282-36e0-4f2a-8124-cd7517e97083');",
]

output = []
for idx, q in enumerate(queries):
    cmd = ["npx", "wrangler", "d1", "execute", "DB", "--remote", f"--command={q}", "--config=../Health_APP_WHOP/wrangler.toml"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    output.append(f"=== Query {idx} ===")
    output.append(res.stdout)

with open("scratch/francis_relations_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
