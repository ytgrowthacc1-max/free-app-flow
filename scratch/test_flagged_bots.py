import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import requests
from execution.whop_auth import is_token_expired

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

bad_bots = [
    "user_01Ekaefl3QSTM",
    "user_0Ll0BPufaOuQZ",
    "user_7ziL4hNckh6Ei",
    "user_FLtuSxu5Uetoy",
    "user_GkYvyusezUmAz",
    "user_n6db6yj3utlJf",
    "user_QuVGhaKJDTJyi",
    "user_test_star_bot"
]

print("--- Testing Flagged Bots ---", flush=True)
for bot_id in bad_bots:
    pfile = os.path.join(bots_dir, bot_id, "profile.json")
    if not os.path.exists(pfile):
        continue
    with open(pfile, "r") as f:
        pdata = json.load(f)
    
    oauth = pdata.get("oauth_token", "")
    exp = is_token_expired(oauth) if oauth else True
    print(f"\nBot {pdata.get('bot_username')} ({bot_id}): expired={exp}", flush=True)
    
    bot_path = os.path.join(bots_dir, bot_id)
    comp_id = None
    for item in os.listdir(bot_path):
        if os.path.isdir(os.path.join(bot_path, item)) and os.path.exists(os.path.join(bot_path, item, "company.json")):
            with open(os.path.join(bot_path, item, "company.json"), "r") as cf:
                comp_id = json.load(cf).get("company_id")
            break
            
    if oauth and comp_id:
        r = requests.get(f"https://api.whop.com/api/v1/experiences?company_id={comp_id}", headers={"Authorization": f"Bearer {oauth}"}, timeout=5)
        print(f"  Current OAuth Test: status={r.status_code}", flush=True)
        if r.status_code == 200:
            print(f"  [SUCCESS] OAuth token is ACTUALLY VALID! Found {len(r.json().get('data', []))} experiences", flush=True)
