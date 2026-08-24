import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv("WHOP_API_KEY")
    if not api_key:
        print("No WHOP_API_KEY found in .env")
        return
        
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    product_ids = [
        "prod_idrEecSloni51", # HEXR PRO
        "prod_T6Icayc7fXnLF", # TRADINGPILOTAI
        "prod_vh0ZNaCvmLmKZ"  # VIP Discord Access
    ]
    
    company_id = "biz_BASDu66lnKwq2c"
    url = "https://api.whop.com/api/v1/plans"
    
    for pid in product_ids:
        params = {
            "product_id": pid,
            "account_id": company_id
        }
        print(f"Fetching plans for product {pid} using API Key...")
        resp = requests.get(url, headers=headers, params=params)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"  Error: {resp.text}")

if __name__ == "__main__":
    main()
