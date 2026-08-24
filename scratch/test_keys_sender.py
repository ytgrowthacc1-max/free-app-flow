import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)

target_agent = "user_X1Uk8voCxS7Vs" # @supportpickcity
channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj"

keys = [
    ("WHOP_API_KEY", os.getenv("WHOP_API_KEY")),
    ("WHOP_COMPANY_API_KEY", os.getenv("WHOP_COMPANY_API_KEY")),
    ("App Builders API Key", "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"),
    ("Old Key", "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba")
]

print(f"=== Checking message sender for all API Keys against channel {channel_id} ===")

for name, key in keys:
    if not key:
        continue
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"channel_id": channel_id, "content": "Testing agent sender key"}
    
    res = requests.post("https://api.whop.com/api/v1/messages", headers=headers, json=payload, timeout=5)
    print(f"\n[{name}]: HTTP {res.status_code}")
    if res.status_code in [200, 201]:
        data = res.json()
        uinfo = data.get("user") or {}
        uid = uinfo.get("id")
        uname = uinfo.get("username")
        print(f"   Sender User ID: {uid} (@{uname}) Name: {uinfo.get('name')}")
        if uid == target_agent:
            print(f"   🎉 MATCH FOUND! Key '{name}' posts as Agent {target_agent} (@{uname})!")
    else:
        print(f"   Response: {res.text}")
