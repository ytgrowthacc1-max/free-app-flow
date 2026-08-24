import os
import sys
import requests
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "execution"))
from whop_auth import get_fresh_token

token = get_fresh_token('user_lO14mFc5tBKN3')
headers = {'Authorization': f'Bearer {token}'}

res = requests.get('https://api.whop.com/api/v1/companies', headers=headers)
if res.status_code == 200:
    data = res.json().get('data', [])
    print(f"Total Companies Owned/Joined by @dawnmuros: {len(data)}\n")
    for c in data:
        cid = c.get('id')
        title = c.get('title')
        route = c.get('route')
        print(f"• Name: {title}")
        print(f"  Dashboard Link: https://whop.com/dashboard/{cid}")
        print(f"  Public Page: https://whop.com/{route}\n")
else:
    print("Error:", res.status_code, res.text)
