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
    except Exception as e:
        safe_print(f"[ERROR] Failed to get OAuth token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    # Inspect a specific channel that we know exists and is valid
    channel_id = "feed_1Cc6SM2ZBDCmXfUTC2MbhD"
    url = f"https://api.whop.com/api/v1/dm_channels/{channel_id}"
    
    safe_print(f"[INFO] Fetching channel details from {url}...")
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        safe_print("[SUCCESS] Channel details:")
        safe_print(json.dumps(resp.json(), indent=2))
    else:
        safe_print(f"[ERROR] Failed to fetch channel: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    main()
