import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import requests
from execution.whop_auth import is_token_expired, get_fresh_token

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

print("--- Testing Bot Token Health ---")
for bot_id in os.listdir(bots_dir):
    pfile = os.path.join(bots_dir, bot_id, "profile.json")
    if not os.path.exists(pfile):
        continue
    with open(pfile, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    username = data.get("bot_username", bot_id)
    oauth = data.get("oauth_token", "")
    refresh = data.get("refresh_token", "")
    is_inv = data.get("refresh_token_invalid", False)
    
    expired = is_token_expired(oauth) if oauth else True
    
    if is_inv or expired:
        print(f"Bot: {username} ({bot_id}) | Expired: {expired} | Flagged Invalid: {is_inv}", flush=True)
        continue
        
    try:
        token = get_fresh_token(bot_id)
        # Find a company for this bot
        bot_path = os.path.join(bots_dir, bot_id)
        comp_id = None
        for item in os.listdir(bot_path):
            if os.path.isdir(os.path.join(bot_path, item)) and os.path.exists(os.path.join(bot_path, item, "company.json")):
                with open(os.path.join(bot_path, item, "company.json"), "r") as cf:
                    comp_id = json.load(cf).get("company_id")
                break
                
        if not comp_id:
            print(f"  [NO COMPANY] {username} ({bot_id})", flush=True)
            continue
            
        r = requests.get(f"https://api.whop.com/api/v1/experiences?company_id={comp_id}", headers={"Authorization": f"Bearer {token}"}, timeout=5)
        if r.status_code == 200:
            exps = r.json().get("data", [])
            print(f"  [SUCCESS] {username} ({bot_id}): Token VALID! Found {len(exps)} experiences for {comp_id}", flush=True)
        else:
            print(f"  [API FAIL] {username} ({bot_id}): Status {r.status_code} - {r.text[:150]}", flush=True)
    except Exception as e:
        print(f"  [ERROR] {username}: {e}", flush=True)
