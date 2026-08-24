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
    
    bot_user_id = "user_P5obcMW3vIrZ8" # appdevelopment
    try:
        user_token = get_fresh_token(bot_user_id)
        safe_print(f"[INFO] Successfully retrieved fresh OAuth token for appdevelopment ({bot_user_id}).")
    except Exception as e:
        safe_print(f"[ERROR] Failed to get OAuth token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    # Fetch companies
    companies_url = "https://api.whop.com/api/v1/companies"
    safe_print(f"[INFO] Fetching companies...")
    comp_resp = requests.get(companies_url, headers=headers)
    if comp_resp.status_code != 200:
        safe_print(f"[ERROR] Failed to fetch companies: {comp_resp.status_code} - {comp_resp.text}")
        return

    companies = comp_resp.json().get("data", [])
    safe_print(f"[INFO] Found {len(companies)} companies: {[c.get('id') for c in companies]}")

    for company in companies:
        company_id = company.get("id")
        company_name = company.get("title")
        safe_print(f"\n--- Checking Company: {company_name} ({company_id}) ---")

        # Fetch DM channels for this company if we can filter by company
        # Note: /dm_channels returns DM channels, let's see if we can filter by company_id
        dm_channels_url = "https://api.whop.com/api/v1/dm_channels"
        params = {"company_id": company_id, "first": 80}
        resp = requests.get(dm_channels_url, headers=headers, params=params)
        
        if resp.status_code != 200:
            safe_print(f"[ERROR] Failed to fetch DM channels for company {company_id}: {resp.status_code} - {resp.text}")
            continue

        channels = resp.json().get("data", [])
        safe_print(f"[INFO] Scanning {len(channels)} channels in {company_name}...")

        found = False
        for idx, chan in enumerate(channels):
            chan_str = json.dumps(chan).lower()
            if "bigwlt" in chan_str:
                safe_print(f"\n[FOUND] Match found in Channel [{idx}] (ID: {chan.get('id')}):")
                safe_print(json.dumps(chan, indent=2))
                found = True
                
        if not found:
            safe_print(f"[INFO] 'bigwlt' was NOT found in any DM channels of company {company_name}.")

if __name__ == "__main__":
    main()
