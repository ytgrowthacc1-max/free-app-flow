import os
import sys
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
sys.path.append(os.path.join(os.getcwd(), 'execution'))
from whop_auth import get_fresh_token

bot_user_id = os.getenv("BOT_USER_ID")
token = get_fresh_token(bot_user_id) if bot_user_id else get_fresh_token()
exp_id = os.getenv("WHOP_EXPERIENCE_ID")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

url = f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&limit=5"
r = requests.get(url, headers=headers)
if r.status_code == 200:
    res = r.json()
    print("Response keys:", list(res.keys()))
    for key in res:
        if key != 'data':
            print(f"{key}: {res[key]}")
else:
    print(f"Error: {r.status_code} - {r.text}")
