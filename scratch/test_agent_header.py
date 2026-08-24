import os
import sys
import requests
import json
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

load_dotenv(override=True)

api_key = os.getenv("WHOP_API_KEY")
channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj" # Pick City support channel
agent_id = "user_X1Uk8voCxS7Vs"

print(f"=== Testing agent selection for user_X1Uk8voCxS7Vs ===")

variations = [
    ("Payload: agent_id", {}, {"channel_id": channel_id, "content": "Test agent message", "agent_id": agent_id}),
    ("Payload: agent_user_id", {}, {"channel_id": channel_id, "content": "Test agent message", "agent_user_id": agent_id}),
    ("Payload: sender_user_id", {}, {"channel_id": channel_id, "content": "Test agent message", "sender_user_id": agent_id}),
    ("Header: Whop-Agent-Id", {"Whop-Agent-Id": agent_id}, {"channel_id": channel_id, "content": "Test agent message"}),
    ("Header: X-Whop-Agent-Id", {"X-Whop-Agent-Id": agent_id}, {"channel_id": channel_id, "content": "Test agent message"}),
    ("Header: X-Agent-Id", {"X-Agent-Id": agent_id}, {"channel_id": channel_id, "content": "Test agent message"}),
]

for name, custom_headers, payload in variations:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **custom_headers
    }
    try:
        res = requests.post("https://api.whop.com/api/v1/messages", headers=headers, json=payload, timeout=5)
        print(f"\n[{name}]: HTTP {res.status_code}")
        if res.status_code in [200, 201]:
            data = res.json()
            user_info = data.get("user") or {}
            print(f"   Returned Sender User: {user_info.get('id')} (@{user_info.get('username')})")
            if user_info.get('id') == agent_id:
                print(f"   🎉 EXACT MATCH FOR AGENT {agent_id}!")
        else:
            print(f"   Response: {res.text}")
    except Exception as e:
        print(f"   Exception: {e}")
