import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = "npx wrangler pages deployment list --project-name health-app-whop --json"
res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True)
if res.returncode != 0:
    print("Error:", res.stderr)
    sys.exit(1)

deployments = json.loads(res.stdout)
print("Latest 5 deployments:")
for d in deployments[:5]:
    print(f"ID: {d['Id']}")
    print(f"  Environment: {d['Environment']}")
    print(f"  Branch: {d['Branch']}")
    print(f"  Source: {d.get('Source')}")
    print(f"  Deployment URL: {d['Deployment']}")
    print(f"  Status: {d['Status']}")
    print()
