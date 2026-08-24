import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

sub_payloads = [
    {"profile_picture": {"url": avatar_url}},
    {"profile_picture": {"id": avatar_url}},
    {"profile_picture": {"image_url": avatar_url}},
    {"profile_picture": {"file_id": avatar_url}},
    {"profile_picture": {"src": avatar_url}},
    {"user": {"profile_picture": avatar_url}},
    {"user": {"profile_picture_url": avatar_url}},
    {"user": {"avatar_url": avatar_url}}
]

for p in sub_payloads:
    r = requests.patch("https://api.whop.com/v1/users/me", headers=headers, json=p)
    print(f"Payload: {p} | Status: {r.status_code} | Text: {r.text[:300]}")
