import os
import requests
from dotenv import load_dotenv

# Ensure the execution directory is in path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))

try:
    from whop_auth import get_fresh_token
except ImportError:
    from execution.whop_auth import get_fresh_token

load_dotenv()

def main():
    try:
        token = get_fresh_token()
    except Exception as e:
        print(f"[ERROR] Failed to get fresh token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://api.whop.com/api/v1/me"
    print(f"[INFO] Fetching user info from {url}...")
    try:
        r = requests.get(url, headers=headers)
        print(f"[STATUS] {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    main()
