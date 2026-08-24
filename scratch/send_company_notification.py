import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WHOP_API_KEY")
company_id = os.getenv("WHOP_COMPANY_ID")
bot_user_id = os.getenv("BOT_USER_ID")

url = "https://api.whop.com/api/v1/notifications"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "company_id": company_id,
    "user_ids": [bot_user_id] if bot_user_id else None,
    "title": "Click this to test redirect ⚡",
    "subtitle": "Testing ngrok tunnel",
    "content": "This notification has rest_path set to /settings/billing. It should open your app at ngrok and redirect you.",
    "rest_path": "/settings/billing"
}

print(f"Sending test notification with rest_path targeting Company ID: {company_id}...")
r = requests.post(url, headers=headers, json=payload)
print("Status Code:", r.status_code)
try:
    print("Response JSON:", json.dumps(r.json(), indent=2))
except Exception:
    print("Response Text:", r.text)
