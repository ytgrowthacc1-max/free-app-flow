import subprocess
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

DEPLOYMENT_ID = "14114d70-5adc-4a7a-82c7-0811b160b389"
print(f"Tailing deployment: {DEPLOYMENT_ID}")
print(">>> OPEN THE DASHBOARD IN YOUR BROWSER NOW <<<")
print("Waiting 40 seconds for requests...\n")

cmd = f'npx wrangler pages deployment tail {DEPLOYMENT_ID} --project-name health-app-whop --config=../Health_APP_WHOP/wrangler.toml --format=json'
proc = subprocess.Popen(
    cmd, shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=r"c:\Python\WHOP AUTOMATION AGENTIC"
)

all_lines = []
start = time.time()
while time.time() - start < 40:
    raw = proc.stdout.readline()
    if not raw:
        time.sleep(0.1)
        continue
    line = raw.decode("utf-8", errors="replace").strip()
    all_lines.append(line)
    if not line:
        continue
    try:
        entry = json.loads(line)
        url = entry.get("request", {}).get("url", "")
        status = entry.get("response", {}).get("status", "?")
        outcome = entry.get("outcome", "ok")
        exceptions = entry.get("exceptions", [])
        logs = entry.get("logs", [])

        if "/api/" in url or exceptions:
            print(f"\n[{status}] {url} | outcome={outcome}")
            for ex in exceptions:
                print(f"  EXCEPTION: {ex}")
            for lg in logs:
                msgs = lg.get("message", [])
                level = lg.get("level", "log")
                if level in ("error", "warn") or any("error" in str(m).lower() or "prisma" in str(m).lower() for m in msgs):
                    print(f"  {level.upper()}: {msgs}")
    except json.JSONDecodeError:
        low = line.lower()
        if any(k in low for k in ["error", "exception", "prisma", "fail", "500"]):
            print("RAW:", line[:500])

proc.terminate()
print(f"\n--- Done. Captured {len(all_lines)} raw lines ---")

# Save full output
with open("scratch/tail_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_lines))
print("Full output saved to scratch/tail_output.txt")
