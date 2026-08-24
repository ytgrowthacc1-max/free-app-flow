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
channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj"
target_agent_id = "user_X1Uk8voCxS7Vs" # supportpickcity

print(f"=== Testing sender identity change to agent {target_agent_id} (@supportpickcity) ===")

variations = [
    ("Payload: agent_id", {}, {"channel_id": channel_id, "content": "Test supportpickcity agent", "agent_id": target_agent_id}),
    ("Payload: agent_user_id", {}, {"channel_id": channel_id, "content": "Test supportpickcity agent", "agent_user_id": target_agent_id}),
    ("Payload: user_id", {}, {"channel_id": channel_id, "content": "Test supportpickcity agent", "user_id": target_agent_id}),
    ("Payload: author_id", {}, {"channel_id": channel_id, "content": "Test supportpickcity agent", "author_id": target_agent_id}),
    ("Header: Whop-Agent-Id", {"Whop-Agent-Id": target_agent_id}, {"channel_id": channel_id, "content": "Test supportpickcity agent"}),
    ("Header: X-Whop-Agent-Id", {"X-Whop-Agent-Id": target_agent_id}, {"channel_id": channel_id, "content": "Test supportpickcity agent"}),
    ("Header: X-Agent-Id", {"X-Agent-Id": target_agent_id}, {"channel_id": channel_id, "content": "Test supportpickcity agent"}),
    ("Header: Whop-User-Id", {"Whop-User-Id": target_agent_id}, {"channel_id": channel_id, "content": "Test supportpickcity agent"}),
    ("Header: X-On-Behalf-Of", {"X-On-Behalf-Of": target_agent_id}, {"channel_id": channel_id, "content": "Test supportpickcity agent"}),
]

for name, custom_headers, payload in variations:
    headers = {
        "Authorization": f"Bearer {app_builders_key}",
        "Content-Type": "application/json",
        **custom_headers
    }
    try:
        res = requests.post("https://api.whop.com/api/v1/messages", headers=headers, json=payload, timeout=5)
        print(f"\n[{name}]: HTTP {res.status_code}")
        if res.status_code in [200, 201]:
            data = res.json()
            uinfo = data.get("user") or {}
            print(f"   Returned Sender User ID: {uinfo.get('id')} (@{uinfo.get('username')}) Name: {uinfo.get('name')}")
            if uinfo.get('id') == target_agent_id:
                print(f"   🎉 MATCH! Successfully posted as @supportpickcity ({target_agent_id})!")
        else:
            print(f"   Response: {res.text}")
    except Exception as e:
        print(f"   Exception: {e}")
