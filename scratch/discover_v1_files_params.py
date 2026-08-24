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

# Test different parameter combinations
test_bodies = [
    {},
    {"filename": "avatar.jpg"},
    {"name": "avatar.jpg"},
    {"file": "avatar.jpg"},
    {"filename": "avatar.jpg", "visibility": "public"},
    {"filename": "avatar.jpg", "custom_type": "profile_picture"},
    {"filename": "avatar.jpg", "file_type": "image"},
]

for idx, b in enumerate(test_bodies, 1):
    r = requests.post("https://api.whop.com/v1/files", headers=headers, json=b)
    print(f"Body #{idx}: {b} | Status: {r.status_code} | Text: {r.text[:300]}")
