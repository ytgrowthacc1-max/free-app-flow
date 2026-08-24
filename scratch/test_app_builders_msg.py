import os
import sys
import requests
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

app_builders_key = "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"
channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj" # Pick City support channel

headers = {
    "Authorization": f"Bearer {app_builders_key}",
    "Content-Type": "application/json"
}

payload = {
    "channel_id": channel_id,
    "content": "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\nThat's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\nOne week, $19.99. You'll see why:\nhttps://whop.com/pickcity/weekly-95/?a=bigwlt\n\nThank me later."
}

print(f"=== Testing Message Dispatch using app_builders API Key ({app_builders_key[:15]}...) ===")
res = requests.post("https://api.whop.com/api/v1/messages", headers=headers, json=payload, timeout=10)
print(f"HTTP Status {res.status_code}: {res.text}")

if res.status_code in [200, 201]:
    data = res.json()
    user_info = data.get("user") or {}
    print(f"\n🎉 SUCCESS! Message Delivered!")
    print(f"   Sender User ID: {user_info.get('id')}")
    print(f"   Sender Name/Username: {user_info.get('name')} (@{user_info.get('username')})")
