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
comp_id = os.getenv("WHOP_COMPANY_ID")
r = requests.get("https://api.whop.com/api/v1/experiences", headers=headers, params={"company_id": comp_id, "first": 40})
if r.status_code == 200:
    for exp in r.json().get("data", []):
        app = exp.get("app") or {}
        print(f"Name: {exp.get('name')} | ID: {exp.get('id')} | App Name: {app.get('name')} | App ID: {app.get('id')}")
else:
    print(r.status_code, r.text)
