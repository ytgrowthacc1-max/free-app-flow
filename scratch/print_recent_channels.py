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

    dm_channels_url = "https://api.whop.com/api/v1/dm_channels"
    params = {"first": 50}
    resp = requests.get(dm_channels_url, headers=headers, params=params)
    
    if resp.status_code != 200:
        safe_print(f"[ERROR] Failed to fetch DM channels: {resp.status_code} - {resp.text}")
        return

    channels = resp.json().get("data", [])
    safe_print(f"[INFO] Listing first {len(channels)} channels for appdevelopment:")
    for idx, chan in enumerate(channels):
        chan_id = chan.get("id")
        title = chan.get("title")
        custom_title = chan.get("custom_title")
        participants = chan.get("participants", [])
        
        participant_names = []
        for p in participants:
            p_user = p.get("user", {})
            p_name = p_user.get("name") or p_user.get("username") or p.get("user_id")
            participant_names.append(p_name)
            
        safe_print(f"[{idx}] ID: {chan_id}, Title: {title or custom_title}, Participants: {participant_names}")

if __name__ == "__main__":
    main()
