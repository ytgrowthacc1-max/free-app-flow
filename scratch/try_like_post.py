import os
import requests
from dotenv import load_dotenv

# Ensure the execution directory is in path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))

from whop_auth import get_fresh_token

load_dotenv()

def main():
    try:
        token = get_fresh_token()
    except Exception as e:
        print(f"[ERROR] Failed to get fresh token: {e}")
        return

    url = "https://api.whop.com/api/v1/reactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Target post
    payload = {
        "resource_id": "post_1CcuUUc8HJCAQQnYiokvTe",
        "emoji": ":heart:"
    }

    print(f"[INFO] Sending reaction (like) to post_1CcuUUc8HJCAQQnYiokvTe...")
    try:
        r = requests.post(url, headers=headers, json=payload)
        print(f"[STATUS] {r.status_code}")
        print(f"[RESPONSE] {r.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    main()
