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
        safe_print(f"[ERROR] Failed to get OAuth token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    # Fetch DM channels
    dm_channels_url = "https://api.whop.com/api/v1/dm_channels"
    params = {"first": 80}
    resp = requests.get(dm_channels_url, headers=headers, params=params)
    
    if resp.status_code != 200:
        safe_print(f"[ERROR] Failed to fetch DM channels: {resp.status_code} - {resp.text}")
        return

    channels = resp.json().get("data", [])
    safe_print(f"[INFO] Found {len(channels)} channels. Scanning their messages for 'bigwlt'...")

    target_channel_id = None
    
    for idx, chan in enumerate(channels):
        chan_id = chan.get("id")
        chan_name = chan.get("name") or "Unnamed"
        
        # Fetch messages for this channel
        messages_url = "https://api.whop.com/api/v1/messages"
        msg_params = {"channel_id": chan_id, "first": 20}
        msg_resp = requests.get(messages_url, headers=headers, params=msg_params)
        
        if msg_resp.status_code != 200:
            continue
            
        messages = msg_resp.json().get("data", [])
        
        # Check authors of all messages in this channel
        for msg in messages:
            msg_user = msg.get("user", {})
            m_uid = msg_user.get("id")
            m_uname = msg_user.get("username")
            
            if m_uid == "user_yZDoWcnQS2LaN" or (m_uname and "bigwlt" in m_uname.lower()):
                safe_print(f"\n[MATCH FOUND] Channel ID: {chan_id} ({chan_name})")
                safe_print(f"Message content: {msg.get('content')}")
                safe_print(f"Message user ID: {m_uid}, Username: {m_uname}")
                target_channel_id = chan_id
                break
                
        if target_channel_id:
            break
            
    if not target_channel_id:
        safe_print("[INFO] No channel found with any message from/to 'bigwlt'.")

if __name__ == "__main__":
    main()
