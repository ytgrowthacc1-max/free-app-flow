import os
import sys
import requests
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))
from whop_auth import get_fresh_token

load_dotenv()

def main():
    try:
        token = get_fresh_token()
    except Exception as e:
        print(f"[ERROR] Failed to get fresh token: {e}")
        bots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profiles", "bots")
        for b in os.listdir(bots_dir):
            pfile = os.path.join(bots_dir, b, "profile.json")
            if os.path.exists(pfile):
                try:
                    with open(pfile, "r") as f:
                        data = json.load(f)
                    if data.get("refresh_token") and not data.get("refresh_token_invalid"):
                        token = get_fresh_token(data["bot_user_id"])
                        print(f"[INFO] Using token for bot: {data['bot_username']}")
                        break
                except Exception:
                    continue
        else:
            print("[ERROR] No valid bot token found.")
            return

    post_id = "post_1Ccw72vtpnGLTJmrtyoxUT"
    url = "https://api.whop.com/api/v1/reactions"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "resource_id": post_id
    }

    print(f"[INFO] Fetching reactions for {post_id}...")
    try:
        r = requests.get(url, headers=headers, params=params)
        print("Status:", r.status_code)
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print("Error:", r.text)
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    main()
