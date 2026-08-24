import os
import sys
import requests
import json
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from execution.whop_auth import get_fresh_token

channel_id = "feed_1Cdb8g6w7TDsyWBiotLPit"
api_key = "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"
bot_user_id = "user_JPHEqzhggecW9"  # sidneysanders61 (Best Offers profile)

print("--- 1. Testing message send via API Key (App/Bot System Identity) ---")
url = "https://api.whop.com/api/v1/messages"
headers_api = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload1 = {
    "channel_id": channel_id,
    "content": "Hey @gloriarussell3c! Test support chat message from Best Offers (sent via App System Identity)."
}
res1 = requests.post(url, headers=headers_api, json=payload1, timeout=10)
print(f"API Key Send HTTP Status {res1.status_code}: {res1.text}")


print("\n--- 2. Testing message send via sidneysanders61 OAuth Token (User Identity) ---")
try:
    user_token = get_fresh_token(bot_user_id)
    headers_user = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    payload2 = {
        "channel_id": channel_id,
        "content": "Hey @gloriarussell3c! Test support chat message from Best Offers (sent via @sidneysanders61)."
    }
    res2 = requests.post(url, headers=headers_user, json=payload2, timeout=10)
    print(f"User OAuth Send HTTP Status {res2.status_code}: {res2.text}")
except Exception as e:
    print(f"Error getting user token: {e}")
