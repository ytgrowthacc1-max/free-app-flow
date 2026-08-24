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
    try:
        user_token = get_fresh_token()
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
    safe_print(f"[INFO] Inspecting {len(channels)} channels...")

    for idx, chan in enumerate(channels):
        # Print the whole channel JSON nicely formatted
        safe_print(f"=== Channel [{idx}] ===")
        safe_print(json.dumps(chan, indent=2))
        safe_print("=" * 40)

if __name__ == "__main__":
    main()
