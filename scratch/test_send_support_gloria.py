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

load_dotenv(override=True)

company_id = "biz_R3lCX4ljztxERk"  # Best Offers
target_user_id = "user_fdWsHxrBCGa62"  # @gloriarussell3c
bot_user_id = "user_JPHEqzhggecW9"  # sidneysanders61 (Best Offers account)

print(f"=== Testing Best Offers Support Chat Pipeline for @gloriarussell3c ===")

# Step 1: Create Channel using WHOP_API_KEY
api_key = os.getenv("WHOP_API_KEY")
print(f"1. Creating support channel for company '{company_id}' & user '{target_user_id}'...")
url_chan = "https://api.whop.com/api/v1/support_channels"
headers_api = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload_chan = {
    "company_id": company_id,
    "user_id": target_user_id
}
res_chan = requests.post(url_chan, headers=headers_api, json=payload_chan, timeout=10)

if res_chan.status_code in [200, 201]:
    chan_id = res_chan.json().get("id")
    print(f"   [SUCCESS] Support Channel ready: {chan_id}")
    
    # Step 2: Send Message as sidneysanders61
    print(f"\n2. Obtaining fresh OAuth token for sidneysanders61 ({bot_user_id})...")
    user_token = get_fresh_token(bot_user_id)
    headers_user = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    
    url_msg = "https://api.whop.com/api/v1/messages"
    payload_msg = {
        "channel_id": chan_id,
        "content": "Hey @gloriarussell3c! Support chat messaging from Best Offers account is live and fully operational."
    }
    
    print("3. Dispatching message to support channel...")
    res_msg = requests.post(url_msg, headers=headers_user, json=payload_msg, timeout=10)
    
    if res_msg.status_code in [200, 201]:
        print(f"   [SUCCESS] Message delivered! Response ID: {res_msg.json().get('id')}")
        print("\n=== SUMMARY: TEST DELIVERED SUCCESSFULLY ===")
    else:
        print(f"   [ERROR] Failed to send message: {res_msg.status_code} - {res_msg.text}")
else:
    print(f"   [ERROR] Failed to create channel: {res_chan.status_code} - {res_chan.text}")
