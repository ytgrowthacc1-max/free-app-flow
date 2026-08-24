import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("WHOP_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("=== Testing minting / fetching access token for Agent user_X1Uk8voCxS7Vs ===")

endpoints = [
    ("POST /user_tokens", "https://api.whop.com/api/v1/user_tokens", {"user_id": "user_X1Uk8voCxS7Vs"}),
    ("POST /oauth/token", "https://api.whop.com/api/v1/oauth/token", {"grant_type": "client_credentials", "user_id": "user_X1Uk8voCxS7Vs"}),
    ("POST /agent_tokens", "https://api.whop.com/api/v1/agent_tokens", {"agent_id": "user_X1Uk8voCxS7Vs"}),
    ("POST /tokens", "https://api.whop.com/api/v1/tokens", {"user_id": "user_X1Uk8voCxS7Vs"}),
]

for name, url, payload in endpoints:
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"\n[{name}]: HTTP {res.status_code}")
        print(f"   Response: {res.text}")
    except Exception as e:
        print(f"   Exception: {e}")
