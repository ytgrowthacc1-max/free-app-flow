import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))
from whop_auth import get_fresh_token

load_dotenv()

def main():
    bot_user_id = "user_0Ll0BPufaOuQZ"  # estellalynch
    token = get_fresh_token(bot_user_id)
    if not token:
        print("Failed to get token")
        return
        
    experience_id = "exp_KgzMrM89tl4khe"
    post_id = "post_1Ccw8CbFbRKxCDXJd8owe6"
    
    url = f"https://api.whop.com/api/v1/forum_posts/{post_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "experience_id": experience_id
    }
    
    r = requests.get(url, headers=headers, params=params)
    print("Status code:", r.status_code)
    try:
        data = r.json()
        print("Title:", data.get("title").encode('ascii', 'replace').decode('ascii'))
        print("Content:", (data.get("content") or "").encode('ascii', 'replace').decode('ascii'))
        # Print keys to be safe
        print("Keys present in response:", list(data.keys()))
    except Exception as e:
        print("Error parsing:", e)

if __name__ == "__main__":
    main()
