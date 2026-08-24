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
bot_user_id = "user_JPHEqzhggecW9"  # sidneysanders61
api_key = os.getenv("WHOP_API_KEY")

channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj"

print(f"=== Sending Pick City Outreach to Support Channel {channel_id} ===")

message_text = (
    "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\n"
    "That's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\n"
    "One week, $19.99. You'll see why:\n"
    "https://whop.com/pickcity/weekly-95/?a=bigwlt\n\n"
    "Thank me later."
)

# 1. Send via Bot Profile (@sidneysanders61)
print(f"1. Fetching fresh token for bot @sidneysanders61 ({bot_user_id})...")
token = get_fresh_token(bot_user_id)
headers_user = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

url_msg = "https://api.whop.com/api/v1/messages"
payload = {
    "channel_id": channel_id,
    "content": message_text
}

print("2. Dispatching message as @sidneysanders61...")
res = requests.post(url_msg, headers=headers_user, json=payload, timeout=10)
print(f"User Message HTTP Status {res.status_code}: {res.text}")

if res.status_code in [200, 201]:
    msg_id = res.json().get("id")
    print(f"\n🎉 SUCCESS! Pick City outreach message delivered to @gloriarussell3c!")
    print(f"   Channel ID: {channel_id}")
    print(f"   Message ID: {msg_id}")
