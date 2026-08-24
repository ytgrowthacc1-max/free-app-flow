import os
import requests
import json
from dotenv import load_dotenv

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def main():
    load_dotenv()
    
    # App API Key or Company API Key
    api_key = os.getenv("WHOP_COMPANY_API_KEY") or os.getenv("WHOP_API_KEY")
    # Company ID (biz_g3xtLNhhkuw2dD or from env)
    company_id = os.getenv("WHOP_COMPANY_ID")
    # Bot User ID (or any authorized bot user ID, like user_7ziL4hNckh6Ei)
    bot_user_id = os.getenv("BOT_USER_ID") or "user_P5obcMW3vIrZ8" # fallback to appdevelopment
    
    print(f"[INFO] Using App API Key to mint token:")
    print(f"  - Company ID: {company_id}")
    print(f"  - Bot User ID: {bot_user_id}")
    
    # Request access token with support_chat:create scope
    mint_url = "https://api.whop.com/api/v1/access_tokens"
    mint_payload = {
        "company_id": company_id,
        "user_id": bot_user_id,
        "scoped_actions": [
            "chat:message:create",
            "chat:read",
            "support_chat:read",
            "support_chat:message:create",
            "support_chat:create"
        ]
    }
    
    mint_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    r = requests.post(mint_url, headers=mint_headers, json=mint_payload)
    if r.status_code != 200:
        safe_print(f"[ERROR] Token minting failed: {r.status_code} - {r.text}")
        return
        
    mint_data = r.json()
    minted_token = mint_data.get("token")
    safe_print(f"[SUCCESS] Minted token successfully! Scope: {mint_data.get('scopes') or mint_payload['scoped_actions']}")
    
    # Test using this token to create support channel
    create_url = "https://api.whop.com/api/v1/support_channels"
    create_payload = {
        "company_id": company_id,
        "user_id": "user_yZDoWcnQS2LaN" # bigwlt
    }
    
    create_headers = {
        "Authorization": f"Bearer {minted_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n[INFO] Attempting to create support channel for bigwlt...")
    resp = requests.post(create_url, headers=create_headers, json=create_payload)
    if resp.status_code in [200, 201]:
        safe_print(f"[SUCCESS] Created channel successfully:")
        safe_print(json.dumps(resp.json(), indent=2))
    else:
        safe_print(f"[ERROR] Channel creation failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    main()
