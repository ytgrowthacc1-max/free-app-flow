import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

access_token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

endpoints = [
    "https://api.whop.com/api/v2/users/me",
    "https://api.whop.com/api/v2/me",
    "https://api.whop.com/v2/users/me",
    "https://api.whop.com/v2/me",
    "https://api.whop.com/v5/users/me",
    "https://api.whop.com/v5/me",
    "https://api.whop.com/users/me",
    "https://api.whop.com/me"
]

payloads = [
    {"profile_pic_url": avatar_url},
    {"avatar_url": avatar_url},
    {"profile_picture": avatar_url},
    {"profile_pic": avatar_url}
]

for url in endpoints:
    for p in payloads:
        r = requests.patch(url, headers=headers, json=p)
        if r.status_code != 404:
            print(f"[MATCH] URL: {url} | Payload: {p} | Status: {r.status_code} | Text: {r.text[:300]}")
