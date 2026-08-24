import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()
company_id = "biz_78VckYvrZN8g34"  # Pick City | betting community
target_user_id = "user_fdWsHxrBCGa62"

with open("config/whop_apps.json", "r") as f:
    apps = json.load(f)

print(f"=== Checking API keys for support channel creation on {company_id} ===")

keys_to_test = []

if os.getenv("WHOP_API_KEY"):
    keys_to_test.append(("WHOP_API_KEY from .env", os.getenv("WHOP_API_KEY")))
if os.getenv("WHOP_COMPANY_API_KEY"):
    keys_to_test.append(("WHOP_COMPANY_API_KEY from .env", os.getenv("WHOP_COMPANY_API_KEY")))

for app_name, app_data in apps.items():
    if isinstance(app_data, dict) and app_data.get("api_key"):
        keys_to_test.append((f"App '{app_name}'", app_data["api_key"]))

for name, key in keys_to_test:
    url = "https://api.whop.com/api/v1/support_channels"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"company_id": company_id, "user_id": target_user_id}
    res = requests.post(url, headers=headers, json=payload, timeout=5)
    print(f"[{name}]: HTTP {res.status_code} -> {res.text}")
