import os
import requests
import json
from dotenv import load_dotenv

# Ensure execution is in path
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

    post_id = "post_1CcuUUc8HJCAQQnYiokvTe"
    experience_id = "exp_u0AVo0rMf75tep"

    url = f"https://api.whop.com/api/v1/forum_posts/{post_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "experience_id": experience_id
    }

    print(f"[INFO] Fetching post details for {post_id}...")
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
