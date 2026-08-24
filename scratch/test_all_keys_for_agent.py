import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)

target_agent = "user_X1Uk8voCxS7Vs" # @supportpickcity

keys = [
    ("WHOP_API_KEY", os.getenv("WHOP_API_KEY")),
    ("WHOP_COMPANY_API_KEY", os.getenv("WHOP_COMPANY_API_KEY")),
    ("App Builders API Key", "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"),
    ("Old Key", "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba")
]

print(f"=== Checking API keys for Agent {target_agent} (@supportpickcity) ===")

for name, key in keys:
    if not key:
        continue
    headers = {"Authorization": f"Bearer {key}"}
    
    # 1. Test GET /me
    res_me = requests.get("https://api.whop.com/api/v1/me", headers=headers, timeout=5)
    print(f"\n[{name}]: GET /me -> HTTP {res_me.status_code}")
    if res_me.status_code == 200:
        data = res_me.json()
        print(f"   User ID: {data.get('id')} (@{data.get('username')}) Name: {data.get('name')}")
        if data.get('id') == target_agent:
            print(f"   🎉 MATCH! {name} IS AGENT {target_agent}!")
    else:
        print(f"   Response: {res_me.text}")
