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
    
    # Load credentials
    api_key = os.getenv("WHOP_API_KEY")
    company_id = os.getenv("WHOP_COMPANY_ID")
    
    if not api_key:
        safe_print("[ERROR] WHOP_API_KEY must be set in your .env file.")
        return
    if not company_id:
        safe_print("[ERROR] WHOP_COMPANY_ID must be set in your .env file.")
        return

    # Let's try calling GET /members with Company API Key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = "https://api.whop.com/api/v1/members"
    params = {
        "company_id": company_id,
        "first": 100
    }

    safe_print(f"[INFO] Fetching members from {url}...")
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        safe_print(f"[ERROR] Failed to fetch members: {resp.status_code} - {resp.text}")
        return

    data = resp.json()
    members = data.get("data", [])
    safe_print(f"[INFO] Found {len(members)} members in current page.")

    for m in members:
        # Check user structure
        user = m.get("user", {})
        username = user.get("username") or ""
        email = user.get("email") or ""
        name = user.get("name") or ""
        user_id = user.get("id") or ""
        
        if "bigwlt" in username.lower() or "bigwlt" in name.lower() or "bigwlt" in email.lower():
            safe_print(f"[FOUND MEMBER] User ID: {user_id}, Username: {username}, Name: {name}, Email: {email}")
            return
            
    # If not found, let's print all user details of the first 10 members to inspect the fields
    safe_print("[INFO] Did not find any member matching 'bigwlt' in the first 100.")
    safe_print("[INFO] Showing first 5 members:")
    for m in members[:5]:
        user = m.get("user", {})
        safe_print(f" - User ID: {user.get('id')}, Username: {user.get('username')}, Name: {user.get('name')}")

if __name__ == "__main__":
    main()
