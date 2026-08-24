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

content_types = [
    "image/jpeg",
    "image/png",
    "jpeg",
    "png",
    "image/jpg",
    "image/webp"
]

for ct in content_types:
    payload = {
        "filename": "avatar.jpg",
        "content_type": ct,
        "size": 95569
    }
    r = requests.post("https://api.whop.com/v1/files", headers=headers, json=payload)
    print(f"CT: {ct:15} | Status: {r.status_code} | Text: {r.text[:300]}")
