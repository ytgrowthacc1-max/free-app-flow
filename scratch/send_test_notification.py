import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WHOP_API_KEY")
experience_id = "exp_s1uihCgf3s9ChG" # WHOP BOT experience ID
bot_user_id = os.getenv("BOT_USER_ID")

target_url = "https://app.usefastlane.ai/login"
# Base64 encode the URL to bypass Whop stripping protocols/domains
encoded_url = base64.b64encode(target_url.encode('utf-8')).decode('utf-8')

url = "https://api.whop.com/api/v1/notifications"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "experience_id": experience_id,
    "user_ids": [bot_user_id] if bot_user_id else None,
    "title": "Fastlane Login (B64) 🚀",
    "subtitle": "Secure external redirection",
    "content": "Please click here to log into Fastlane. This uses a Base64-encoded path bypass.",
    "rest_path": encoded_url
}

print(f"Sending test notification with Base64 URL: {encoded_url} (points to: {target_url}) using experience ID: {experience_id}...")
r = requests.post(url, headers=headers, json=payload)
print("Status Code:", r.status_code)
try:
    print("Response JSON:", json.dumps(r.json(), indent=2))
except Exception:
    print("Response Text:", r.text)
