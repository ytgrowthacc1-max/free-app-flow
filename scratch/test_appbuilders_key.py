import os
import requests
import json

api_key = "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"
company_id = "biz_R3lCX4ljztxERk"  # Best Offers
target_user_id = "user_fdWsHxrBCGa62"  # @gloriarussell3c

url = "https://api.whop.com/api/v1/support_channels"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "company_id": company_id,
    "user_id": target_user_id
}

print("Testing support channel creation with app_builders API key...")
res = requests.post(url, headers=headers, json=payload, timeout=10)
print(f"HTTP Status {res.status_code}: {res.text}")
