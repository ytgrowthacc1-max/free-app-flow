import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("WHOP_API_KEY")
company_id = "biz_78VckYvrZN8g34" # Pick City
user_id = "viciglos"
sender_agent_id = "user_X1Uk8voCxS7Vs" # @supportpickcity

# Step 1: Create channel using Company API Key (NO X-On-Behalf-Of)
headers_create = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
res_c = requests.post("https://api.whop.com/api/v1/support_channels", headers=headers_create, json={"company_id": company_id, "user_id": user_id})
print(f"Step 1 (Create Channel): HTTP {res_c.status_code}")

if res_c.status_code in [200, 201]:
    channel_id = res_c.json().get("id")
    print(f"Channel ID: {channel_id}")
    
    # Step 2: Send Message into Channel with X-On-Behalf-Of header (Sender = @supportpickcity)
    headers_send = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-On-Behalf-Of": sender_agent_id
    }
    payload_msg = {
        "channel_id": channel_id,
        "content": "Testing automated support outreach message from @supportpickcity!"
    }
    res_m = requests.post("https://api.whop.com/api/v1/messages", headers=headers_send, json=payload_msg)
    print(f"Step 2 (Send Message as Agent): HTTP {res_m.status_code} - {res_m.text}")
