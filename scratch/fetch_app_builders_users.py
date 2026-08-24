import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# We have WHOP_API_KEY / WHOP_COMPANY_API_KEY in .env
# Also let's check App Builders specific key if present
api_key = os.getenv("WHOP_API_KEY")
app_builders_key = "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"
company_id = "biz_Vwsite2gfnFBU2"

keys_to_test = [
    ("Default API Key", api_key),
    ("App Builders Key", app_builders_key)
]

for label, key in keys_to_test:
    if not key:
        continue
    print(f"\n--- Testing {label} ---")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    # Test 1: GET /api/v1/members
    print(f"Querying /api/v1/members?company_id={company_id}...")
    try:
        r = requests.get(f"https://api.whop.com/api/v1/members?company_id={company_id}&first=5", headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Members response sample: {json.dumps(data, indent=2)[:1000]}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

    # Test 2: GET /api/v1/payments
    print(f"\nQuerying /api/v1/payments?company_id={company_id}...")
    try:
        r = requests.get(f"https://api.whop.com/api/v1/payments?company_id={company_id}&first=5", headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Payments response sample: {json.dumps(data, indent=2)[:1000]}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

    # Test 3: GET /api/v1/memberships
    print(f"\nQuerying /api/v1/memberships?company_id={company_id}...")
    try:
        r = requests.get(f"https://api.whop.com/api/v1/memberships?company_id={company_id}&first=5", headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Memberships response sample: {json.dumps(data, indent=2)[:1000]}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")
