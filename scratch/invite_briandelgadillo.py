import os
import requests
from dotenv import load_dotenv

load_dotenv()

user_id = "user_7ziL4hNckh6Ei"
company_id = "biz_g3xtLNhhkuw2dD"

payload = {
    "company_id": company_id,
    "user_id": user_id,
    "role": "owner",
    "send_emails": True
}

api_keys = {
    "WHOP_API_KEY (App Key)": os.getenv("WHOP_API_KEY"),
    "WHOP_COMPANY_API_KEY (Company Key)": os.getenv("WHOP_COMPANY_API_KEY")
}

url = "https://api.whop.com/api/v1/authorized_users"

for name, key in api_keys.items():
    if not key:
        print(f"Skipping {name} (not set)")
        continue
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    print(f"\nAttempting to invite user with {name}...")
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")
