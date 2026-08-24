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

company_id = "biz_78VckYvrZN8g34"  # Pick City | betting community
target_user_id = "user_fdWsHxrBCGa62"  # @gloriarussell3c
bot_user_id = "user_JPHEqzhggecW9"  # sidneysanders61

token = get_fresh_token(bot_user_id)
print(f"--- Got fresh OAuth token for sidneysanders61 ({bot_user_id}) ---")

# 1. Test POST /support_channels with sidneysanders61 OAuth token
url_chan = "https://api.whop.com/api/v1/support_channels"
headers_user = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload_chan = {
    "company_id": company_id,
    "user_id": target_user_id
}

print(f"\n1. Creating/fetching support channel for Pick City ({company_id})...")
res_chan = requests.post(url_chan, headers=headers_user, json=payload_chan, timeout=10)
print(f"User OAuth POST /support_channels HTTP Status {res_chan.status_code}: {res_chan.text}")

if res_chan.status_code not in [200, 201]:
    # Try App API key
    app_key = "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"
    headers_app = {"Authorization": f"Bearer {app_key}", "Content-Type": "application/json"}
    res_app = requests.post(url_chan, headers=headers_app, json=payload_chan, timeout=10)
    print(f"App API Key POST /support_channels HTTP Status {res_app.status_code}: {res_app.text}")
    if res_app.status_code in [200, 201]:
        res_chan = res_app

if res_chan.status_code in [200, 201]:
    chan_id = res_chan.json().get("id")
    print(f"\n[SUCCESS] Support Channel ready: {chan_id}")
    
    # 2. Send Message to support channel
    url_msg = "https://api.whop.com/api/v1/messages"
    payload_msg = {
        "channel_id": chan_id,
        "content": "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\nThat's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\nOne week, $19.99. You'll see why:\nhttps://whop.com/pickcity/weekly-95/?a=bigwlt\n\nThank me later."
    }
    
    print("\n2. Dispatching Pick City outreach message...")
    res_msg = requests.post(url_msg, headers=headers_user, json=payload_msg, timeout=10)
    print(f"Message Send HTTP Status {res_msg.status_code}: {res_msg.text}")
    if res_msg.status_code in [200, 201]:
        print(f"\n🎉 SUCCESS: Message delivered from Pick City | betting community ({company_id})!")
