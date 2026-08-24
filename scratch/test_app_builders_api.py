import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "execution"))
from whop_auth import get_fresh_token

load_dotenv()

bot_id = "user_P5obcMW3vIrZ8"
token = get_fresh_token(bot_id)

print(f"Token obtained: {bool(token)} (length: {len(token) if token else 0})")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

company_id = "biz_Vwsite2gfnFBU2"

endpoints = [
    ("Company Info", f"https://api.whop.com/api/v1/companies/{company_id}"),
    ("Company Public Info", f"https://api.whop.com/api/v1/companies/app-builders-f882"),
    ("List Experiences", f"https://api.whop.com/api/v1/experiences?company_id={company_id}"),
    ("List Members", f"https://api.whop.com/api/v1/members?company_id={company_id}"),
    ("List Memberships", f"https://api.whop.com/api/v1/memberships?company_id={company_id}"),
    ("List Payments", f"https://api.whop.com/api/v1/payments?company_id={company_id}"),
    ("List Users", f"https://api.whop.com/api/v1/users?company_id={company_id}"),
    ("DM Channels", f"https://api.whop.com/api/v1/dm_channels"),
    ("Support Channels", f"https://api.whop.com/api/v1/support_channels?company_id={company_id}")
]

for name, url in endpoints:
    print(f"\n--- {name}: {url} ---")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            formatted = json.dumps(data, indent=2)
            print(f"Response (first 500 chars):\n{formatted[:500]}")
        else:
            print(f"Response: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")
