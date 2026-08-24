import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
api_key = os.getenv("WHOP_API_KEY")
company_id = os.getenv("WHOP_COMPANY_ID")
app_id = os.getenv("WHOP_APP_ID")

url = "https://api.whop.com/api/v1/experiences"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "app_id": app_id,
    "company_id": company_id,
    "name": "WHOP BOT",
    "is_public": True
}

print(f"Attempting to create experience for App: {app_id} under Company: {company_id}...")
print("Payload:", json.dumps(payload, indent=2))

r = requests.post(url, headers=headers, json=payload)
print("Status Code (OAuth):", r.status_code)
try:
    print("Response JSON:", json.dumps(r.json(), indent=2))
except Exception:
    print("Response Text:", r.text)

if r.status_code != 200:
    print("\nRetrying with Developer API Key...")
    headers_api = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    r_api = requests.post(url, headers=headers_api, json=payload)
    print("Status Code (API Key):", r_api.status_code)
    try:
        print("Response JSON:", json.dumps(r_api.json(), indent=2))
    except Exception:
        print("Response Text:", r_api.text)
