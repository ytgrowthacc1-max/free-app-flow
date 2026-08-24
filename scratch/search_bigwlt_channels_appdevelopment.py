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
    
    bot_user_id = "user_P5obcMW3vIrZ8" # appdevelopment
    try:
        user_token = get_fresh_token(bot_user_id)
        safe_print(f"[INFO] Successfully retrieved fresh OAuth token for appdevelopment ({bot_user_id}).")
    except Exception as e:
        safe_print(f"[ERROR] Failed to get OAuth token for appdevelopment: {e}")
        return

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    dm_channels_url = "https://api.whop.com/api/v1/dm_channels"
    params = {"first": 80}
    resp = requests.get(dm_channels_url, headers=headers, params=params)
    
    if resp.status_code != 200:
        safe_print(f"[ERROR] Failed to fetch DM channels: {resp.status_code} - {resp.text}")
        return

    channels = resp.json().get("data", [])
    safe_print(f"[INFO] Scanning {len(channels)} channels for 'bigwlt'...")

    found = False
    for idx, chan in enumerate(channels):
        chan_str = json.dumps(chan).lower()
        if "bigwlt" in chan_str:
            safe_print(f"\n[FOUND] Match found in Channel [{idx}] (ID: {chan.get('id')}):")
            safe_print(json.dumps(chan, indent=2))
            found = True
            
    if not found:
        safe_print("[INFO] 'bigwlt' was NOT found in any DM channels of 'appdevelopment'.")

if __name__ == "__main__":
    main()
