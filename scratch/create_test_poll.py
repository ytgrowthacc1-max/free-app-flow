import os
import requests
from dotenv import load_dotenv
import json
import sys
sys.path.append(os.path.join(os.getcwd(), 'execution'))
from whop_auth import get_fresh_token

load_dotenv()
bot_user_id = os.getenv('BOT_USER_ID')
token = get_fresh_token(bot_user_id)
exp_id = os.getenv("WHOP_EXPERIENCE_ID")

url = "https://api.whop.com/api/v1/forum_posts"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "experience_id": exp_id,
    "title": "Agent Temp Test Poll",
    "content": "This is a temporary test poll to inspect option IDs.",
    "pinned": False,
    "is_mention": False,
    "visibility": "members_only",
    "poll": {
        "options": [
            {"id": "1", "text": "Choice A"},
            {"id": "2", "text": "Choice B"}
        ]
    }
}

r = requests.post(url, headers=headers, json=payload)
print("Status:", r.status_code)
if r.status_code in [200, 201]:
    res = r.json()
    print(json.dumps(res, indent=2))
else:
    print("Error:", r.text)
