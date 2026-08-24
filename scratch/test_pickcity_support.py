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

company_id = "biz_78VckYvrZN8g34"  # Pick City | betting community
target_user_id = "user_fdWsHxrBCGa62"  # @gloriarussell3c
api_key = os.getenv("WHOP_API_KEY")

print(f"=== Testing Support Chat for Pick City ({company_id}) to user {target_user_id} ===")

# 1. Create Support Channel
url_chan = "https://api.whop.com/api/v1/support_channels"
headers_api = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload_chan = {
    "company_id": company_id,
    "user_id": target_user_id
}

print(f"1. Creating support channel with company_id: {company_id}...")
res_chan = requests.post(url_chan, headers=headers_api, json=payload_chan, timeout=10)
print(f"Channel Creation HTTP {res_chan.status_code}: {res_chan.text}")

if res_chan.status_code in [200, 201]:
    chan_id = res_chan.json().get("id")
    print(f"   [SUCCESS] Support Channel ready: {chan_id}")
    
    # 2. Send Message via API Key (System Identity)
    url_msg = "https://api.whop.com/api/v1/messages"
    payload_msg = {
        "channel_id": chan_id,
        "content": "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\nThat's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\nOne week, $19.99. You'll see why:\nhttps://whop.com/pickcity/weekly-95/?a=bigwlt\n\nThank me later."
    }
    
    print("\n2. Sending test message to support channel...")
    res_msg = requests.post(url_msg, headers=headers_api, json=payload_msg, timeout=10)
    print(f"Message Send HTTP {res_msg.status_code}: {res_msg.text}")
    if res_msg.status_code in [200, 201]:
        print("\n🎉 SUCCESS: Message delivered from Pick City | betting community!")
