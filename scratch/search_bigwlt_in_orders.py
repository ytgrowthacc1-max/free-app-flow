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

def main():
    load_dotenv()
    
    api_key = os.getenv("WHOP_API_KEY")
    company_id = os.getenv("WHOP_COMPANY_ID")
    
    if not api_key:
        safe_print("[ERROR] WHOP_API_KEY must be set in your .env file.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = "https://api.whop.com/api/v1/orders"
    params = {
        "company_id": company_id,
        "first": 100
    }

    safe_print(f"[INFO] Fetching orders from {url}...")
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        safe_print(f"[ERROR] Failed to fetch orders: {resp.status_code} - {resp.text}")
        return

    data = resp.json()
    orders = data.get("data", [])
    safe_print(f"[INFO] Found {len(orders)} orders in current page.")

    for o in orders:
        # Check user structure
        user = o.get("user", {})
        username = user.get("username") or ""
        email = user.get("email") or ""
        name = user.get("name") or ""
        user_id = user.get("id") or ""
        
        if "bigwlt" in username.lower() or "bigwlt" in name.lower() or "bigwlt" in email.lower():
            safe_print(f"[FOUND ORDER] User ID: {user_id}, Username: {username}, Name: {name}, Email: {email}")
            return

    safe_print("[INFO] Did not find any order matching 'bigwlt' in the first 100 orders.")

if __name__ == "__main__":
    main()
