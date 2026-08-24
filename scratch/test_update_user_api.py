import os
import sys
import requests
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "execution"))
from whop_auth import get_fresh_token

bot_user_id = "user_lO14mFc5tBKN3" # @dawnmuros ID
token = get_fresh_token(bot_user_id)
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

img_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

endpoints = [
    f"https://api.whop.com/api/v5/users/{bot_user_id}",
    f"https://api.whop.com/api/v1/users/{bot_user_id}",
    f"https://api.whop.com/api/v2/users/{bot_user_id}",
    "https://api.whop.com/api/v5/users/me",
    "https://api.whop.com/api/v1/users/me",
    "https://api.whop.com/api/v2/users/me",
    f"https://api.whop.com/api/beta/users/{bot_user_id}",
    "https://api.whop.com/api/beta/users/me",
    f"https://api.whop.com/api/v5/me",
]

payload_keys = [
    "profile_picture_url",
    "profile_picture",
    "avatar_url",
    "image_url",
    "profile_pic_url",
    "image"
]

for ep in endpoints:
    for key in payload_keys:
        payload = {key: img_url}
        res = requests.patch(ep, json=payload, headers=headers)
        print(f"PATCH {ep} ({key}) -> Status: {res.status_code}")
        if res.status_code in (200, 201):
            print("SUCCESS! Response:", res.text)
            sys.exit(0)
        else:
            print("  Body:", res.text[:200])
