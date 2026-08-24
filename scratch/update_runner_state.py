import sys
import os

with open("execution/run_campaign_outreach.py", "r", encoding="utf-8") as f:
    content = f.read()

state_code = '''
import threading

CAMPAIGN_RUNNER_STATE = {
    "status": "idle",
    "campaign_id": "",
    "campaign_name": "",
    "mode": "DRY RUN",
    "total": 0,
    "processed": 0,
    "successful": 0,
    "failed": 0,
    "current_target": "",
    "logs": [],
    "last_updated": ""
}
STATE_LOCK = threading.Lock()

def add_campaign_log(msg):
    with STATE_LOCK:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{ts}] {msg}"
        CAMPAIGN_RUNNER_STATE["logs"].append(log_line)
        if len(CAMPAIGN_RUNNER_STATE["logs"]) > 250:
            CAMPAIGN_RUNNER_STATE["logs"].pop(0)
        CAMPAIGN_RUNNER_STATE["last_updated"] = datetime.datetime.now().isoformat()
        print(log_line)

def get_campaign_runner_state():
    with STATE_LOCK:
        return dict(CAMPAIGN_RUNNER_STATE)
'''

if "CAMPAIGN_RUNNER_STATE" not in content:
    content = content.replace("CONFIG_PATH =", state_code + "\nCONFIG_PATH =")

with open("execution/run_campaign_outreach.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Added CAMPAIGN_RUNNER_STATE to execution/run_campaign_outreach.py")
