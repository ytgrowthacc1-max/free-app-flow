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

# Fetch users from GET /api/v1/users?company_id=biz_Vwsite2gfnFBU2
url = f"https://api.whop.com/api/v1/users?company_id={company_id}&first=20"
r = requests.get(url, headers=headers)

if r.status_code == 200:
    data = r.json()
    users = data.get("data", [])
    print(f"Total Users fetched: {len(users)}")
    
    results = []
    for u in users:
        user_info = {
            "id": u.get("id"),
            "username": u.get("username"),
            "name": u.get("name"),
            "bio": u.get("bio"),
            "created_at": u.get("created_at"),
            "social_accounts": [
                {
                    "platform": s.get("platform"),
                    "username": s.get("username"),
                    "name": s.get("name"),
                    "external_id": s.get("external_id")
                } for s in u.get("social_accounts", [])
            ],
            "verification": u.get("verification")
        }
        results.append(user_info)
        
    print(json.dumps(results, indent=2))
else:
    print(f"Error fetching users: {r.status_code} - {r.text}")
