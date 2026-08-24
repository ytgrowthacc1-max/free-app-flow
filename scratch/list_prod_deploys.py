import subprocess
import json

cmd = "npx wrangler pages deployment list --project-name health-app-whop --config=../Health_APP_WHOP/wrangler.toml --json"
res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True)
if res.returncode == 0:
    data = json.loads(res.stdout)
    print("Recent Production Deployments:")
    for d in data[:8]:
        if d.get("Environment") == "Production":
            print(f"  ID: {d['Id']} | Created: {d['Status']} | URL: {d['Deployment']}")
else:
    print("Error:", res.stderr)
