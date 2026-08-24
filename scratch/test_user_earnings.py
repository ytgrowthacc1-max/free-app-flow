import os
import sys
import json
import requests

company_api_key = "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba"
company_id = "biz_Vwsite2gfnFBU2"

headers = {
    "Authorization": f"Bearer {company_api_key}",
    "Content-Type": "application/json"
}

# 1. Test user profile endpoints for earnings_usd, total_usd, balances
test_users = [
    ("user_yZDoWcnQS2LaN", "bigwlt"),
    ("user_Ta2Ilej0DUqVq", "scalewdreww"),
    ("user_7ez4Gzsp4wS2L", "therealr1cky"),
    ("user_0Dq4R58QYV613", "focalmarkcc / GoldspireFX"),
    ("user_PN02PGS1ONdKR", "seeyoulaterleaner / Adam Atkinson"),
    ("user_m2hd7s6H2N8m5", "akhileshjat")
]

print("="*80)
print("TESTING USER PROFILE FINANCIAL & EARNINGS DATA (/api/v1/users/{id})")
print("="*80)

for uid, name in test_users:
    print(f"\n--- Checking User: {name} ({uid}) ---")
    url = f"https://api.whop.com/api/v1/users/{uid}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        print(f"  Username: @{data.get('username')}")
        print(f"  Name: {data.get('name')}")
        print(f"  Earnings USD: {data.get('earnings_usd')}")
        print(f"  Total USD: {data.get('total_usd')}")
        print(f"  Whop Partner: {data.get('whop_partner_enabled_at')}")
        print(f"  Balances: {data.get('balances')}")
        print(f"  Verification: {data.get('verification')}")
    else:
        print(f"  Error: {r.status_code} - {r.text}")

print("\n" + "="*80)
print("TESTING MEMBER SPENDING DATA IN COMMUNITY (/api/v1/members & /api/v1/people)")
print("="*80)

# 2. Test spending metrics on members & people in App Builders
members_url = f"https://api.whop.com/api/v1/members?company_id={company_id}&first=10"
r_mem = requests.get(members_url, headers=headers)
if r_mem.status_code == 200:
    for m in r_mem.json().get("data", [])[:5]:
        u = m.get("user") or {}
        print(f"Member: @{u.get('username')} | USD Total Spent: ${m.get('usd_total_spent', 0):.2f} | Tokens: {m.get('company_token_balance')}")

# 3. Test LTV / AOV on people
people_url = f"https://api.whop.com/api/v1/people?company_id={company_id}&order=ltv&direction=desc&first=10"
r_peop = requests.get(people_url, headers=headers)
if r_peop.status_code == 200:
    print("\nTop Spenders / LTV via People API:")
    for p in r_peop.json().get("data", []):
        u = p.get("user") or {}
        print(f"User: @{u.get('username')} ({p.get('name')}) | LTV: ${p.get('ltv', 0):.2f} | AOV: ${p.get('aov', 0):.2f} | Purchases: {p.get('purchase_count')} | Location: {p.get('location', {}).get('country')}")

# 4. Test public web profile endpoint without auth (public scraper / API)
print("\n" + "="*80)
print("TESTING PUBLIC SCRAPED PROFILES")
print("="*80)
public_url = "https://api.whop.com/api/v1/users/user_yZDoWcnQS2LaN"
r_pub = requests.get(public_url)
print("Public User Endpoint (No Auth) Status:", r_pub.status_code)
if r_pub.status_code == 200:
    print(json.dumps(r_pub.json(), indent=2))
