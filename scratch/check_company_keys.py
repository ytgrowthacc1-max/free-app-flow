import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_keys = {
    "WHOP_API_KEY": os.getenv("WHOP_API_KEY"),
    "WHOP_COMPANY_API_KEY": os.getenv("WHOP_COMPANY_API_KEY")
}

for name, key in api_keys.items():
    if not key:
        print(f"{name} is not set")
        continue
    headers = {"Authorization": f"Bearer {key}"}
    print(f"\nQuerying /companies using {name}...")
    try:
        r = requests.get("https://api.whop.com/api/v1/companies", headers=headers)
        print(f"Status Code: {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")
