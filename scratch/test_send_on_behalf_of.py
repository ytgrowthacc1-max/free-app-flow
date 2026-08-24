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

load_dotenv(override=True)

api_key = os.getenv("WHOP_API_KEY")
channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj"
target_agent_id = "user_X1Uk8voCxS7Vs" # @supportpickcity

print(f"=== Testing Message Dispatch as @supportpickcity ({target_agent_id}) via X-On-Behalf-Of ===")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-On-Behalf-Of": target_agent_id
}

message_text = (
    "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\n"
    "That's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\n"
    "One week, $19.99. You'll see why:\n"
    "https://whop.com/pickcity/weekly-95/?a=bigwlt\n\n"
    "Thank me later."
)

payload = {
    "channel_id": channel_id,
    "content": message_text
}

res = requests.post("https://api.whop.com/api/v1/messages", headers=headers, json=payload, timeout=10)
print(f"HTTP Status {res.status_code}: {res.text}")

if res.status_code in [200, 201]:
    data = res.json()
    uinfo = data.get("user") or {}
    print(f"\n🎉 CONFIRMED SUCCESS!")
    print(f"   Message ID: {data.get('id')}")
    print(f"   Sender User ID: {uinfo.get('id')}")
    print(f"   Sender Username: @{uinfo.get('username')}")
    print(f"   Sender Display Name: {uinfo.get('name')}")
