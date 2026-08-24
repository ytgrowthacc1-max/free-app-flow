import subprocess

cmd = ["npx", "wrangler", "d1", "execute", "DB", "--remote", "--command=SELECT id, name, ownerId FROM TrainingProgram;", "--config=../Health_APP_WHOP/wrangler.toml"]
res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
with open("scratch/remote_programs.txt", "w", encoding="utf-8") as f:
    f.write(res.stdout)
