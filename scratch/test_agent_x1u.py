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
agent_user_id = "user_X1Uk8voCxS7Vs"  # New Agent Account
api_key = os.getenv("WHOP_API_KEY")

channel_id = "feed_1CdbJ8yXhr5ZiByohiJsSj"

print(f"=== Testing Pick City Support Message using Agent {agent_user_id} ===")

message_text = (
    "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\n"
    "That's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\n"
    "One week, $19.99. You'll see why:\n"
    "https://whop.com/pickcity/weekly-95/?a=bigwlt\n\n"
    "Thank me later."
)

# Test 1: Send via API Key specifying agent / user if supported or OAuth
print("\n--- Test 1: Trying get_fresh_token for agent_user_id ---")
try:
    token = get_fresh_token(agent_user_id)
    headers_user = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    res = requests.post("https://api.whop.com/api/v1/messages", headers=headers_user, json={"channel_id": channel_id, "content": message_text}, timeout=10)
    print(f"OAuth Message Send HTTP {res.status_code}: {res.text}")
except Exception as e:
    print(f"get_fresh_token failed for {agent_user_id}: {e}")

# Test 2: Send via API Key directly or with user_id header/body
print("\n--- Test 2: Trying API Key dispatch ---")
headers_api = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test sending message via API Key to support channel
payload_api = {
    "channel_id": channel_id,
    "content": message_text,
    "user_id": agent_user_id
}
res_api = requests.post("https://api.whop.com/api/v1/messages", headers=headers_api, json=payload_api, timeout=10)
print(f"API Key Message Send (with user_id) HTTP {res_api.status_code}: {res_api.text}")

if res_api.status_code not in [200, 201]:
    # Test without user_id parameter
    payload_api2 = {
        "channel_id": channel_id,
        "content": message_text
    }
    res_api2 = requests.post("https://api.whop.com/api/v1/messages", headers=headers_api, json=payload_api2, timeout=10)
    print(f"API Key Message Send (standard) HTTP {res_api2.status_code}: {res_api2.text}")
