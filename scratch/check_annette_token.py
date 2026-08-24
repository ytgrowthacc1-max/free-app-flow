import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from whop_auth import get_fresh_token

bot_id = "user_6sYkOfNNp99cV"
token = get_fresh_token(bot_id)

print(f"Token retrieved: {bool(token)}")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("https://api.whop.com/v1/users/me", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"User response: {r.text[:200]}")
