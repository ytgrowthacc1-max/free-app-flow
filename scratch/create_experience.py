import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv
load_dotenv()

from execution.whop_auth import get_fresh_token
token = get_fresh_token()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

company_id = "biz_Vwsite2gfnFBU2" # App Builders
app_id = "app_oPIxXnyEJ8uxNK" # From .env

url = "https://api.whop.com/api/v1/experiences"
payload = {
    "app_id": app_id,
    "company_id": company_id,
    "name": "Outreach Automation Bot",
    "is_public": True
}

print(f"[INFO] Creating experience for App {app_id} in Company {company_id}...")
r = requests.post(url, headers=headers, json=payload)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
