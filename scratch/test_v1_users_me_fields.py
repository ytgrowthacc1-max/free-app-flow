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

field_names = [
    "profile_pic_url",
    "profile_picture_url",
    "avatar_url",
    "profile_picture",
    "avatar",
    "profile_pic",
    "image_url",
    "picture"
]

for field in field_names:
    payload = {field: avatar_url}
    r = requests.patch("https://api.whop.com/v1/users/me", headers=headers, json=payload)
    print(f"Field: {field:22} | Status: {r.status_code} | Text: {r.text[:300]}")
