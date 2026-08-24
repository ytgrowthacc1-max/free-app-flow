import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

company_id = "biz_R3lCX4ljztxERk"

# Load ericdavis8b's oauth token
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
eric_pfile = os.path.join(base_dir, "profiles", "bots", "user_QuVGhaKJDTJyi", "profile.json")
eric_token = None
if os.path.exists(eric_pfile):
    with open(eric_pfile, "r", encoding="utf-8") as f:
        eric_token = json.load(f).get("oauth_token")

tokens = {
    "WHOP_API_KEY (App Key)": os.getenv("WHOP_API_KEY"),
    "WHOP_COMPANY_API_KEY (Company Key)": os.getenv("WHOP_COMPANY_API_KEY"),
    "ericdavis8b OAuth Token": eric_token
}

url = "https://api.whop.com/api/v1/authorized_users"

for name, token in tokens.items():
    if not token:
        print(f"Skipping {name} (not set)")
        continue
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "company_id": company_id
    }
    
    print(f"\nQuerying authorized users with {name}...")
    try:
        r = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")
