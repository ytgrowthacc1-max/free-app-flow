import os
import sys
import requests
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "execution"))
from whop_auth import get_fresh_token

img_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"
bot_user_id = "user_lO14mFc5tBKN3"

token = get_fresh_token(bot_user_id)
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 1. Fetch current me info
print("--- Fetching /me endpoint ---")
r_me = requests.get("https://api.whop.com/api/v1/me", headers=headers)
print("GET /me status:", r_me.status_code)
if r_me.status_code == 200:
    me_data = r_me.json()
    print("User Data:", json.dumps(me_data, indent=2))
else:
    print("Response:", r_me.text)

# Also test GET /users/me or v5/me or GraphQL if applicable
r_me_v5 = requests.get("https://api.whop.com/api/v5/me", headers=headers)
print("\nGET /v5/me status:", r_me_v5.status_code)

# 2. Test updating profile via PATCH /me or PATCH /users/me or PATCH /user
payloads = [
    {"profile_picture_url": img_url},
    {"avatar_url": img_url},
    {"profile_pic_url": img_url},
    {"profile_picture": img_url},
    {"profile": {"picture_url": img_url}}
]

endpoints = [
    "https://api.whop.com/api/v1/me",
    "https://api.whop.com/api/v1/users/me",
    "https://api.whop.com/api/v5/me"
]

print("\n--- Testing update profile endpoints ---")
for ep in endpoints:
    for p in payloads:
        res = requests.patch(ep, json=p, headers=headers)
        print(f"PATCH {ep} with payload {p}: Status {res.status_code}")
        if res.status_code in (200, 201):
            print("SUCCESS:", res.text)
            break
        else:
            print("  Res:", res.text[:200])
