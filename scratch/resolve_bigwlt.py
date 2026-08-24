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
    
    api_key = os.getenv("WHOP_API_KEY")
    user_id_or_username = "bigwlt"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try calling GET /users/{username}
    url = f"https://api.whop.com/api/v1/users/{user_id_or_username}"
    safe_print(f"[INFO] Fetching user info from {url}...")
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        safe_print(f"[SUCCESS] Resolved username {user_id_or_username}:")
        safe_print(json.dumps(data, indent=2))
    else:
        safe_print(f"[ERROR] Failed to resolve username: {resp.status_code} - {resp.text}")
        
        # Try using OAuth token instead of API key
        try:
            user_token = get_fresh_token()
            headers_oauth = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            }
            safe_print(f"[INFO] Trying with user OAuth token instead...")
            resp_oauth = requests.get(url, headers=headers_oauth)
            if resp_oauth.status_code == 200:
                safe_print(f"[SUCCESS] Resolved username using OAuth:")
                safe_print(json.dumps(resp_oauth.json(), indent=2))
            else:
                safe_print(f"[ERROR] OAuth attempt also failed: {resp_oauth.status_code} - {resp_oauth.text}")
        except Exception as e:
            safe_print(f"[ERROR] OAuth token refresh failed: {e}")

if __name__ == "__main__":
    main()
