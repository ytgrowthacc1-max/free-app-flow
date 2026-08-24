import requests
import json
import os
from dotenv import load_dotenv

sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(os.path.join(sys_path, "execution"))

try:
    from whop_auth import get_fresh_token
except ImportError:
    from execution.whop_auth import get_fresh_token

load_dotenv()

def fetch_plans_with_params(headers, params):
    url = "https://api.whop.com/api/v1/plans"
    print(f"Testing with params: {params}...")
    try:
        resp = requests.get(url, headers=headers, params=params)
        print(f"  Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            plans = data.get("data", [])
            print(f"  [SUCCESS] Found {len(plans)} plans:")
            for p in plans:
                name = p.get("name") or "Standard"
                price = p.get("price")
                currency = p.get("currency") or "USD"
                btype = p.get("billing_type")
                info = f"{price} {currency} ({btype})"
                print(f"    - [{p.get('id')}] {name}: {info}")
            return True
        else:
            print(f"  Error: {resp.text[:300]}")
    except Exception as e:
        print(f"  Exception: {e}")
    return False

def main():
    try:
        oauth_token = get_fresh_token()
    except Exception as e:
        print(f"Failed to refresh OAuth token: {e}")
        oauth_token = None
        
    if not oauth_token:
        print("No OAuth token available")
        return
        
    headers = {
        "Authorization": f"Bearer {oauth_token}"
    }
    
    prod_id = "prod_idrEecSloni51" # HEXR PRO
    owner_id = "user_bRSoO3KwDgW5D"
    company_id = "biz_BASDu66lnKwq2c"
    
    # Try multiple variations of passing IDs
    fetch_plans_with_params(headers, {"product_id": prod_id, "account_id": owner_id})
    fetch_plans_with_params(headers, {"product_id": prod_id, "account_id": company_id})
    fetch_plans_with_params(headers, {"product_id": prod_id, "company_id": company_id})
    fetch_plans_with_params(headers, {"product_id": prod_id, "account_id": "user_ImMeqYlxMpCgP"}) # Our bot user ID
    fetch_plans_with_params(headers, {"product_id": prod_id, "account_id": "biz_A9VwR0dUntlCoX"}) # Our company ID

if __name__ == "__main__":
    main()
