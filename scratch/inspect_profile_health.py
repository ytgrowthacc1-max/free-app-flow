import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath("execution"))
from whop_auth import is_token_expired, get_fresh_token

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

print("Checking Bot Profiles:")
if os.path.exists(bots_dir):
    for bot_id in os.listdir(bots_dir):
        bot_path = os.path.join(bots_dir, bot_id)
        if not os.path.isdir(bot_path):
            continue
        pfile = os.path.join(bot_path, "profile.json")
        if not os.path.exists(pfile):
            print(f"  Bot {bot_id}: profile.json missing!")
            continue
        with open(pfile, "r", encoding="utf-8") as f:
            bot_data = json.load(f)
        
        bot_username = bot_data.get("bot_username", "Unknown Bot")
        token = bot_data.get("oauth_token", "")
        
        # Check health
        health = "INVALID"
        try:
            if not is_token_expired(token):
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.get("https://api.whop.com/api/v1/users/me", headers=headers, timeout=5)
                if resp.status_code == 200:
                    health = "VALID"
                else:
                    health = f"INVALID (HTTP {resp.status_code})"
            else:
                # Expired - try refresh
                fresh = get_fresh_token(bot_id)
                if fresh:
                    health = "VALID (Refreshed)"
                else:
                    health = "INVALID (Failed refresh)"
        except Exception as e:
            health = f"ERROR ({e})"
            
        print(f"  Bot: @{bot_username} (ID: {bot_id}) | Health: {health}")
        # Print associated companies
        for item in os.listdir(bot_path):
            comp_path = os.path.join(bot_path, item)
            if os.path.isdir(comp_path):
                cfile = os.path.join(comp_path, "company.json")
                if os.path.exists(cfile):
                    with open(cfile, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                    print(f"    - Community: {cdata.get('company_name')} (ID: {cdata.get('company_id')}) | Hidden: {cdata.get('hidden')}")
else:
    print("No profiles/bots directory found.")
