import os
import sys
import requests
import json
from dotenv import load_dotenv

# Ensure execution directory is in path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))
from whop_auth import get_fresh_token

load_dotenv()

def main():
    try:
        token = get_fresh_token()
    except Exception as e:
        print(f"[ERROR] Failed to get fresh token: {e}")
        # Try listing bots to get any bot token
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
    experience_id = "exp_KgzMrM89tl4khe"

    url = f"https://api.whop.com/api/v1/forum_posts/{post_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "experience_id": experience_id
    }

    print(f"[INFO] Fetching post details for {post_id} from experience {experience_id}...")
    try:
        r = requests.get(url, headers=headers, params=params)
        print("Status:", r.status_code)
        if r.status_code == 200:
            post_data = r.json()
            print(json.dumps(post_data, indent=2))
        else:
            print("Error:", r.text)
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    main()
