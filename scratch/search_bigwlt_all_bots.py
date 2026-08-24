import os
import requests
import json
from dotenv import load_dotenv

# Import auth helper from execution directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from execution.whop_auth import get_fresh_token

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def main():
    load_dotenv()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bots_dir = os.path.join(base_dir, "profiles", "bots")
    
    if not os.path.exists(bots_dir):
        safe_print(f"[ERROR] Bots directory not found at {bots_dir}")
        return
        
    bot_profiles = os.listdir(bots_dir)
    safe_print(f"[INFO] Found bot profiles: {bot_profiles}")
    
    for bot_id in bot_profiles:
        profile_path = os.path.join(bots_dir, bot_id, "profile.json")
        if not os.path.exists(profile_path):
            continue
            
        with open(profile_path, "r", encoding="utf-8") as f:
            pdata = json.load(f)
            
        username = pdata.get("bot_username", bot_id)
        safe_print(f"\n==================================================")
        safe_print(f"Checking Bot: {username} ({bot_id})")
        safe_print(f"==================================================")
        
        try:
            user_token = get_fresh_token(bot_id)
        except Exception as e:
            safe_print(f"[ERROR] Failed to get OAuth token for {username}: {e}")
            continue
            
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        dm_channels_url = "https://api.whop.com/api/v1/dm_channels"
        params = {"first": 80}
        resp = requests.get(dm_channels_url, headers=headers, params=params)
        
        if resp.status_code != 200:
            safe_print(f"[ERROR] Failed to fetch DM channels: {resp.status_code} - {resp.text}")
            continue
            
        channels = resp.json().get("data", [])
        safe_print(f"[INFO] Retrieved {len(channels)} channels.")
        
        found = False
        for idx, chan in enumerate(channels):
            chan_str = json.dumps(chan).lower()
            if "bigwlt" in chan_str or "yzdowcnqs2lan" in chan_str:
                safe_print(f"\n[FOUND] Match found in Channel [{idx}] (ID: {chan.get('id')}):")
                safe_print(json.dumps(chan, indent=2))
                found = True
                
        if not found:
            safe_print(f"[INFO] No channels containing 'bigwlt' or 'user_yZDoWcnQS2LaN' found for {username}.")

if __name__ == "__main__":
    main()
