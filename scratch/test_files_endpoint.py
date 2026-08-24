import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

access_token = data.get("oauth_token")

candidates = [
    "https://api.whop.com/v5/files",
    "https://api.whop.com/files",
    "https://api.whop.com/v2/files",
    "https://api.whop.com/api/v5/files",
    "https://whop.com/api/v5/files"
]

payload = {
    "filename": "avatar.jpg",
    "visibility": "public"
}

for url in candidates:
    r = requests.post(url, headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}, json=payload)
    print(f"URL: {url} | Status: {r.status_code} | Text: {r.text[:300]}")
