import os
import requests
import json
from dotenv import load_dotenv

# Import auth helper from execution directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from execution.whop_auth import get_fresh_token

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def try_create(headers, label):
    company_id = os.getenv("WHOP_COMPANY_ID")
    url = "https://api.whop.com/api/v1/support_channels"
    
    payload = {
        "company_id": company_id,
        "user_id": "user_yZDoWcnQS2LaN"
    }
    
    safe_print(f"\n[INFO] Attempting to create support channel using {label}...")
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        safe_print(f"[SUCCESS] {label} created support channel:")
        safe_print(json.dumps(resp.json(), indent=2))
        return resp.json().get("id")
    else:
        safe_print(f"[ERROR] {label} failed: {resp.status_code} - {resp.text}")
        return None

def main():
    load_dotenv()
    
    api_key = os.getenv("WHOP_API_KEY")
    
    # 1. Try with Company API Key
    headers_api = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    chan_id = try_create(headers_api, "Company API Key")
    if chan_id:
        return
        
    # 2. Try with appdevelopment OAuth Token
    try:
        user_token = get_fresh_token("user_P5obcMW3vIrZ8") # appdevelopment bot user
        headers_oauth = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        try_create(headers_oauth, "appdevelopment User OAuth Token")
    except Exception as e:
        safe_print(f"[ERROR] Failed to get appdevelopment OAuth token: {e}")

if __name__ == "__main__":
    main()
