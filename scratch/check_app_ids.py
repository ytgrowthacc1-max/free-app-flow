import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
company_id = os.getenv("WHOP_COMPANY_ID")

url = f"https://api.whop.com/api/v1/experiences?company_id={company_id}"
headers = {
    "Authorization": f"Bearer {token}"
}

r = requests.get(url, headers=headers)
if r.status_code == 200:
    exps = r.json().get("data", [])
    for exp in exps:
        print(f"\n==========================================")
        print(f"Name: {exp.get('name')}")
        print(f"ID: {exp.get('id')}")
        app_info = exp.get("app", {})
        print(f"App Name: {app_info.get('name')}")
        print(f"App ID: {app_info.get('id')}")
        print(f"App Client ID: {app_info.get('client_id')}")
else:
    print("Error:", r.text)
