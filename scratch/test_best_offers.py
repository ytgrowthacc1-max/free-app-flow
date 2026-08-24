import os
import requests
import json
from dotenv import load_dotenv

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def test_auth(label, token, company_id):
    if not token:
        print(f"[{label}] token not found, skipping.")
        return False
        
    url = "https://api.whop.com/api/v1/support_channels"
    payload = {
        "company_id": company_id,
        "user_id": "user_yZDoWcnQS2LaN" # bigwlt
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n[TEST] {label} with Company {company_id}:")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in [200, 201]:
            safe_print(f"  [SUCCESS] Created/retrieved support channel: {resp.json().get('id')}")
            return True
        else:
            safe_print(f"  [FAILED] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        safe_print(f"  [ERROR] {e}")
        return False

def main():
    load_dotenv()
    
    # 1. Company API Keys from env
    api_key = os.getenv("WHOP_API_KEY")
    comp_api_key = os.getenv("WHOP_COMPANY_API_KEY")
    
    # 2. OAuth token for appdevelopment from env
    appdev_token = os.getenv("WHOP_OAUTH_TOKEN")
    
    # 3. OAuth token for sidneysanders61 (Best Offers bot) from profile.json
    sidney_token = None
    try:
        profile_path = "profiles/bots/user_JPHEqzhggecW9/profile.json"
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                sidney_token = data.get("oauth_token")
    except Exception as e:
        print(f"[WARNING] Failed to load sidneysanders61 token: {e}")
        
    company_id = "biz_R3lCX4ljztxERk" # Best Offers
    
    test_auth("WHOP_API_KEY (Env)", api_key, company_id)
    test_auth("WHOP_COMPANY_API_KEY (Env)", comp_api_key, company_id)
    test_auth("appdevelopment Token (Env)", appdev_token, company_id)
    test_auth("sidneysanders61 Token (Profile)", sidney_token, company_id)

if __name__ == "__main__":
    main()
