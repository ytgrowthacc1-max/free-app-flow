import os
import sys
import requests
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))
from whop_auth import get_fresh_token

load_dotenv()

def main():
    # Use stacybrown12 (index 3 in valid list) or another bot to test
    bots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profiles", "bots")
    bot_folders = sorted([f for f in os.listdir(bots_dir) if os.path.isdir(os.path.join(bots_dir, f))])
    
    # Find a bot we haven't used, or use one we have. Estellalynch (user_0Ll0BPufaOuQZ)
    bot_user_id = "user_0Ll0BPufaOuQZ"
    token = get_fresh_token(bot_user_id)
    if not token:
        print("Failed to get token for bot")
        return
        
    post_id = "post_1Ccw7Z3hZDrv8izt7rJThh"
    url = "https://api.whop.com/api/v1/reactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try voting for option "2" (e.g. "I hit the limit almost daily")
    payload = {
        "resource_id": post_id,
        "poll_option_id": "2"
    }
    
    print(f"Submitting vote for option '2' on {post_id} from user {bot_user_id}...")
    r = requests.post(url, headers=headers, json=payload)
    print("Status code:", r.status_code)
    print("Response JSON:")
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)

if __name__ == "__main__":
    main()
