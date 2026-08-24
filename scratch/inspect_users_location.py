import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "execution"))
from whop_auth import get_fresh_token

bot_id = "user_P5obcMW3vIrZ8"
token = get_fresh_token(bot_id)
company_id = "biz_Vwsite2gfnFBU2"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Fetch all users from GET /api/v1/users?company_id=biz_Vwsite2gfnFBU2
url = f"https://api.whop.com/api/v1/users?company_id={company_id}&first=10"
r = requests.get(url, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    users = data.get("data", [])
    print(f"Fetched {len(users)} users.")
    for idx, u in enumerate(users[:5]):
        print(f"\n--- USER {idx+1}: {u.get('username')} ({u.get('name')}) ---")
        print(json.dumps(u, indent=2))
        
        # Test individual user endpoint
        user_id = u.get("id")
        if user_id:
            u_resp = requests.get(f"https://api.whop.com/api/v1/users/{user_id}", headers=headers)
            print(f"  [Individual /users/{user_id} Status: {u_resp.status_code}]")
            if u_resp.status_code == 200:
                print("  Individual user data keys:", list(u_resp.json().keys()))
                print("  Individual user data:", json.dumps(u_resp.json(), indent=2))
else:
    print(f"Failed: {r.text}")
