import os
import requests
from dotenv import load_dotenv

load_dotenv()

def try_with_oauth():
    # Ensure the execution directory is in path
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))

    try:
        from whop_auth import get_fresh_token
        token = get_fresh_token()
    except Exception as e:
        print(f"[ERROR] Failed to get fresh token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://api.whop.com/api/v1/companies"
    print(f"\n[INFO] Try with OAuth Token: Fetching from {url}...")
    try:
        r = requests.get(url, headers=headers)
        print(f"[STATUS] {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            companies = data.get("data", [])
            print(f"[SUCCESS] Found {len(companies)} companies:")
            for company in companies:
                print(f" - Name: {company.get('title') or company.get('name')}")
                print(f"   ID: {company.get('id')}")
        else:
            print(f"[ERROR] Failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

def try_with_api_key():
    api_key = os.getenv("WHOP_API_KEY")
    if not api_key:
        print("[ERROR] WHOP_API_KEY not found in .env")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = "https://api.whop.com/api/v1/companies"
    print(f"\n[INFO] Try with Company API Key: Fetching from {url}...")
    try:
        r = requests.get(url, headers=headers)
        print(f"[STATUS] {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            companies = data.get("data", [])
            print(f"[SUCCESS] Found {len(companies)} companies:")
            for company in companies:
                print(f" - Name: {company.get('title') or company.get('name')}")
                print(f"   ID: {company.get('id')}")
        else:
            print(f"[ERROR] Failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    try_with_oauth()
    try_with_api_key()
