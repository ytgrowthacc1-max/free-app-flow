import subprocess
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

DEPLOYMENT_ID = "14114d70-5adc-4a7a-82c7-0811b160b389"
print(f"Tailing deployment: {DEPLOYMENT_ID}")
print("Please open the dashboard now in your browser and try to load workouts/exercises.")
print("Waiting 60 seconds...")

cmd = f'npx wrangler pages deployment tail {DEPLOYMENT_ID} --project-name health-app-whop --config=../Health_APP_WHOP/wrangler.toml --format=json'
proc = subprocess.Popen(
    cmd, shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=r"c:\Python\WHOP AUTOMATION AGENTIC"
)

start = time.time()
lines = []
while time.time() - start < 60:
    raw = proc.stdout.readline()
    if raw:
        line = raw.decode("utf-8", errors="replace").strip()
        lines.append(line)
        if "{" in line:
            try:
                import json
                data = json.loads(line)
                url = data.get("request", {}).get("url", "")
                status = data.get("response", {}).get("status", "")
                logs = data.get("logs", [])
                exceptions = data.get("exceptions", [])
                print(f"Captured: [{status}] {url}")
                if exceptions:
                    print(f"  Exceptions: {exceptions}")
                for lg in logs:
                    print(f"  LOG: {lg}")
            except Exception as e:
                pass
        else:
            if "error" in line.lower() or "exception" in line.lower():
                print(f"RAW: {line}")

proc.terminate()
with open("scratch/tail_60s_raw.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Finished tail. Saved {len(lines)} lines to scratch/tail_60s_raw.txt")
