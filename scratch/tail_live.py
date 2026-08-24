import subprocess
import time
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

url = "https://14114d70.health-app-whop.pages.dev"
cmd = f"npx wrangler pages deployment tail {url} --project-name health-app-whop --format=json"
print("Running:", cmd)
print(">>> PLEASE OPEN THE DASHBOARD IN YOUR BROWSER NOW (LOAD THE EXERCISES/CLIENTS PAGE) <<<")
print("Waiting 60 seconds for requests to stream in...\n")

proc = subprocess.Popen(
    cmd, shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=r"c:\Python\WHOP AUTOMATION AGENTIC"
)

captured = []
start = time.time()
while time.time() - start < 60:
    line = proc.stdout.readline()
    if line:
        decoded = line.decode("utf-8", errors="replace").strip()
        captured.append(decoded)
        if "{" in decoded:
            try:
                entry = json.loads(decoded)
                req_url = entry.get("request", {}).get("url", "")
                status = entry.get("response", {}).get("status", "?")
                outcome = entry.get("outcome", "ok")
                exceptions = entry.get("exceptions", [])
                logs = entry.get("logs", [])
                
                print(f"\n[{status}] {req_url} (outcome: {outcome})")
                for ex in exceptions:
                    print(f"  EXCEPTION: {ex}")
                for lg in logs:
                    print(f"  LOG ({lg.get('level')}): {lg.get('message')}")
            except Exception as e:
                pass
        else:
            if "error" in decoded.lower() or "exception" in decoded.lower():
                print("RAW ERROR:", decoded[:400])
    else:
        time.sleep(0.1)

proc.terminate()
with open("scratch/tail_live_logs.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(captured))
print(f"\nDone. Captured {len(captured)} log entries. Full logs saved to scratch/tail_live_logs.txt")
