import subprocess
import time
import sys
import threading
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

# Tail the production URL
url = "https://health-app-whop.pages.dev"
print(f"Tailing pages URL: {url}")

cmd = f'npx wrangler pages deployment tail {url} --project-name health-app-whop --config=../Health_APP_WHOP/wrangler.toml --format=json'
proc = subprocess.Popen(
    cmd, shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=r"c:\Python\WHOP AUTOMATION AGENTIC"
)

captured = []

def reader():
    for raw in proc.stdout:
        line = raw.decode("utf-8", errors="replace").strip()
        if line:
            captured.append(line)
            try:
                import json
                entry = json.loads(line)
                req_url = entry.get("request", {}).get("url", "")
                status = entry.get("response", {}).get("status", "?")
                outcome = entry.get("outcome", "ok")
                exceptions = entry.get("exceptions", [])
                logs = entry.get("logs", [])
                
                print(f"[{status}] {req_url} (outcome: {outcome})")
                for ex in exceptions:
                    print(f"  EXCEPTION: {ex}")
                for lg in logs:
                    print(f"  LOG ({lg.get('level')}): {lg.get('message')}")
            except:
                if "error" in line.lower() or "exception" in line.lower() or "fail" in line.lower():
                    print("RAW:", line[:300])

t = threading.Thread(target=reader, daemon=True)
t.start()

# Wait 3 seconds for tail to connect
time.sleep(3)

# Send request to trigger log
print("Sending request to trigger dashboard endpoint...")
try:
    req = urllib.request.Request(
        "https://health-app-whop.pages.dev/api/dashboard",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    urllib.request.urlopen(req, timeout=10)
except Exception as e:
    print(f"Request result (expected to fail/succeed): {e}")

# Wait another 5 seconds for tail output
time.sleep(5)

proc.terminate()
print("Done tailing.")
