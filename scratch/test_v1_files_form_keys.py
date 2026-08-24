import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"
img_bytes = requests.get(avatar_url).content

form_keys = ["file", "attachment", "image", "upload", "profile_picture", "avatar"]

for key in form_keys:
    r = requests.post(
        "https://api.whop.com/v1/files",
        headers={"Authorization": f"Bearer {token}"},
        files={key: ("avatar.jpg", img_bytes, "image/jpeg")},
        data={"custom_type": "profile_picture"}
    )
    print(f"Key: {key:18} | Status: {r.status_code} | Text: {r.text[:300]}")
