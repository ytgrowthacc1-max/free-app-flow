import os
import sys
import json
import requests

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

company_api_key = "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba"
company_id = "biz_Vwsite2gfnFBU2"

headers = {
    "Authorization": f"Bearer {company_api_key}",
    "Content-Type": "application/json"
}

# 1. Fetch top spenders in App Builders cleanly
people_url = f"https://api.whop.com/api/v1/people?company_id={company_id}&order=ltv&direction=desc&first=10"
r = requests.get(people_url, headers=headers)
if r.status_code == 200:
    print("--- TOP COMMUNITY SPENDERS IN APP BUILDERS ---")
    for p in r.json().get("data", []):
        if p.get("ltv", 0) > 0 or p.get("purchase_count", 0) > 0:
            u = p.get("user") or {}
            print(f"User: @{u.get('username')} ({p.get('name')}) | LTV: ${p.get('ltv', 0):.2f} | AOV: ${p.get('aov', 0):.2f} | Purchases: {p.get('purchase_count')} | Location: {p.get('location', {}).get('country')}")

# 2. Fetch public company statistics
print("\n--- PUBLIC CREATOR / COMPANY METRICS ---")
comp_resp = requests.get("https://api.whop.com/api/v1/companies/app-builders-f882")
if comp_resp.status_code == 200:
    c = comp_resp.json()
    print(f"Company: {c.get('title')}")
    print(f"Member Count: {c.get('member_count')}")
    print(f"Published Reviews: {c.get('published_reviews_count')}")
    print(f"Verified: {c.get('verified')}")
