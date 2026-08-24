import os
import sys
import requests
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "execution"))
sys.path.insert(0, base_dir)

from whop_auth import get_fresh_token
from dashboard_server import import_bot_and_companies

bot_user_id = "user_lO14mFc5tBKN3"
bot_username = "dawnmuros"

token = get_fresh_token(bot_user_id)
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("https://api.whop.com/api/v1/companies", headers=headers)

if resp.status_code == 200:
    companies = resp.json().get("data", [])
    print(f"Fetched {len(companies)} companies from Whop API for @{bot_username}.")
    import_bot_and_companies(token, "", bot_user_id, bot_username, companies)
    print("Sync complete!")
else:
    print(f"Error fetching companies: {resp.status_code} - {resp.text}")
