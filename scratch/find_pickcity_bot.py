import os
import sys
import requests
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from execution.whop_auth import get_fresh_token

target_company = "biz_78VckYvrZN8g34"
bots_dir = os.path.join(BASE_DIR, "profiles", "bots")

print(f"--- Searching all bot profiles for company access: {target_company} ---")

found = []
for bot_folder in os.listdir(bots_dir):
    pfile = os.path.join(bots_dir, bot_folder, "profile.json")
    if not os.path.exists(pfile):
        continue
    
    try:
        with open(pfile, "r", encoding="utf-8") as f:
            pdata = json.load(f)
        username = pdata.get("bot_username") or bot_folder
        if pdata.get("refresh_token_invalid"):
            continue
            
        token = get_fresh_token(bot_folder)
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(f"https://api.whop.com/api/v1/experiences?company_id={target_company}", headers=headers, timeout=5)
        if res.status_code == 200:
            exp_data = res.json().get("data", [])
            print(f"[MATCH!] Bot '{username}' ({bot_folder}) HAS ACCESS to {target_company}! ({len(exp_data)} experiences)")
            found.append((bot_folder, username))
        else:
            res2 = requests.get(f"https://api.whop.com/api/v1/companies/{target_company}", headers=headers, timeout=5)
            if res2.status_code == 200:
                print(f"[MATCH!] Bot '{username}' ({bot_folder}) HAS ACCESS to company profile {target_company}!")
                found.append((bot_folder, username))
            else:
                print(f"[NO ACCESS] Bot '{username}' ({bot_folder})")
    except Exception as e:
        print(f"[SKIP] Error checking bot {bot_folder}: {e}")

print(f"\nTotal Matching Bots found for {target_company}: {len(found)}")
