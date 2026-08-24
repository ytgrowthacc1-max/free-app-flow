import os
import requests
import json
from dotenv import load_dotenv

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def test_combination(api_key_name, api_key, company_id_name, company_id):
    if not api_key:
        print(f"[{api_key_name}] not set, skipping.")
        return False
        
    url = "https://api.whop.com/api/v1/support_channels"
    payload = {
        "company_id": company_id,
        "user_id": "user_yZDoWcnQS2LaN" # bigwlt
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n[TEST] {api_key_name} ({api_key[:12]}...) with {company_id_name} ({company_id})")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in [200, 201]:
            safe_print(f"  [SUCCESS] Created channel! Channel ID: {resp.json().get('id')}")
            return True
        else:
            safe_print(f"  [FAILED] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        safe_print(f"  [ERROR] {e}")
        return False

def main():
    load_dotenv()
    
    keys = {
        "WHOP_API_KEY": os.getenv("WHOP_API_KEY"),
        "WHOP_COMPANY_API_KEY": os.getenv("WHOP_COMPANY_API_KEY")
    }
    
    companies = {
        "ToolSuite": "biz_PGrBvrTmJFHAaL",
        "Study Dropshipping": "biz_g3xtLNhhkuw2dD"
    }
    
    for key_name, key in keys.items():
        for comp_name, comp_id in companies.items():
            test_combination(key_name, key, comp_name, comp_id)

if __name__ == "__main__":
    main()
