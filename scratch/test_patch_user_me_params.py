import requests
import json
import base64

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

access_token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

# Download image bytes
img_bytes = requests.get(avatar_url).content
b64_img = base64.b64encode(img_bytes).decode('utf-8')
data_uri = f"data:image/jpeg;base64,{b64_img}"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

payloads = [
    {"profile_picture_url": avatar_url},
    {"avatar_url": avatar_url},
    {"profile_picture": avatar_url},
    {"profile_picture": {"url": avatar_url}},
    {"profile_picture": {"base64": b64_img}},
    {"profile_picture_url": data_uri},
    {"avatar": avatar_url},
    {"profile_pic": avatar_url}
]

for idx, p in enumerate(payloads, 1):
    r = requests.patch("https://api.whop.com/api/v5/users/me", headers=headers, json=p)
    print(f"Payload #{idx}: {list(p.keys())[0]} | Status: {r.status_code} | Text: {r.text[:300]}")
