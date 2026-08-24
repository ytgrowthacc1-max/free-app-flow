import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("WHOP_API_KEY")
print(f"WHOP_API_KEY loaded: {api_key[:10]}..." if api_key else "NO WHOP_API_KEY")

company_id = "biz_78VckYvrZN8g34" # Pick City
user_id = "viciglos" # or user_fdWsHxrBCGa62

# Test 1: Standard Company API Key without header
headers1 = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
res1 = requests.post("https://api.whop.com/api/v1/support_channels", headers=headers1, json={"company_id": company_id, "user_id": user_id})
print(f"Test 1 (Standard API Key): HTTP {res1.status_code} - {res1.text}")

# Test 2: API Key with X-On-Behalf-Of header
headers2 = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-On-Behalf-Of": "user_X1Uk8voCxS7Vs"
}
res2 = requests.post("https://api.whop.com/api/v1/support_channels", headers=headers2, json={"company_id": company_id, "user_id": user_id})
print(f"Test 2 (X-On-Behalf-Of user_X1Uk8voCxS7Vs): HTTP {res2.status_code} - {res2.text}")

# Test 3: OAuth Token if available
try:
    import sys
    sys.path.append("execution")
    from whop_auth import get_fresh_token
    oauth_token = get_fresh_token()
    headers3 = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json"
    }
    res3 = requests.post("https://api.whop.com/api/v1/support_channels", headers=headers3, json={"company_id": company_id, "user_id": user_id})
    print(f"Test 3 (OAuth User Token): HTTP {res3.status_code} - {res3.text}")
except Exception as e:
    print(f"Test 3 (OAuth Token): Error getting token - {e}")
