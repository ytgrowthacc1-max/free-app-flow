import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

endpoints = [
    "https://api.whop.com/v1/attachments",
    "https://api.whop.com/v1/uploads",
    "https://api.whop.com/v1/direct_uploads",
    "https://whop.com/api/v1/direct_uploads",
    "https://whop.com/rails/active_storage/direct_uploads",
    "https://api.whop.com/v1/files"
]

payload = {
    "filename": "avatar.jpg",
    "content_type": "image/jpeg",
    "byte_size": 95569
}

for url in endpoints:
    r = requests.post(url, headers=headers, json=payload)
    print(f"URL: {url} | Status: {r.status_code} | Text: {r.text[:300]}")
