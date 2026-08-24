import os
import requests
from dotenv import load_dotenv

# Ensure the execution directory is in the import path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.whop_auth import get_fresh_token

load_dotenv()

try:
    token = get_fresh_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("[INFO] Fetching companies...")
    r = requests.get("https://api.whop.com/api/v1/companies", headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get("data", [])
        print(f"Found {len(data)} companies:")
        for c in data:
            print(f"- ID: {c.get('id')} | Name: {c.get('name')} | Title: {c.get('title')}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Exception: {e}")
