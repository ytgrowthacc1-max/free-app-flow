import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

header_combos = [
    {"Authorization": f"Bearer {token}"},
    {"x-whop-user-token": token},
    {"x-user-token": token},
    {"Authorization": f"User {token}"},
    {"Authorization": token}
]

urls = [
    "https://api.whop.com/v2/users/me",
    "https://api.whop.com/v2/me",
    "https://data.whop.com/api/v2/users/me",
    "https://api.whop.com/v1/users/me"
]

payload = {"profile_pic_url": avatar_url}

for url in urls:
    for h in header_combos:
        h_copy = h.copy()
        h_copy["Content-Type"] = "application/json"
        r = requests.patch(url, headers=h_copy, json=payload)
        if r.status_code != 404:
            print(f"URL: {url} | Header: {list(h.keys())[0]} | Status: {r.status_code} | Text: {r.text[:300]}")
