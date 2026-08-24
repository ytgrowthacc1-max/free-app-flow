import os
import sys
import requests
import json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from execution.whop_auth import get_fresh_token

load_dotenv()

company_id = "biz_R3lCX4ljztxERk"  # Best Offers
target_user_id = "user_fdWsHxrBCGa62"  # @gloriarussell3c
bot_user_id = "user_JPHEqzhggecW9"  # sidneysanders61

token = get_fresh_token(bot_user_id)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("=== 1. Checking GET /support_channels ===")
res_list = requests.get(f"https://api.whop.com/api/v1/support_channels?company_id={company_id}", headers=headers)
print(f"GET /support_channels HTTP {res_list.status_code}: {res_list.text[:500]}")

print("\n=== 2. Checking GET /dm_channels ===")
res_dms = requests.get("https://api.whop.com/api/v1/dm_channels", headers=headers)
print(f"GET /dm_channels HTTP {res_dms.status_code}: {res_dms.text[:500]}")

print("\n=== 3. Testing POST /dm_channels ===")
payload_dm = {
    "user_ids": [target_user_id]
}
res_createdm = requests.post("https://api.whop.com/api/v1/dm_channels", headers=headers, json=payload_dm)
print(f"POST /dm_channels HTTP {res_createdm.status_code}: {res_createdm.text[:500]}")
