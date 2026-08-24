import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WHOP_API_KEY")
channel_id = "feed_1Cdb8g6w7TDsyWBiotLPit"

url = f"https://api.whop.com/api/v1/messages?channel_id={channel_id}"
headers = {
    "Authorization": f"Bearer {api_key}"
}

res = requests.get(url, headers=headers)
print(f"HTTP {res.status_code}")
if res.status_code == 200:
    messages = res.json().get("data", [])
    print(f"Total messages in channel: {len(messages)}")
    for m in messages:
        sender = m.get("user", {}).get("username") or m.get("user", {}).get("name") or "System/App"
        print(f"- [{m.get('created_at')}] From: {sender} | Content: {m.get('content')}")
