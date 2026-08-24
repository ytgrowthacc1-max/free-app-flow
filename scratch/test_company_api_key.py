import os
import sys
import json
import requests

api_key = "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

company_id = "biz_Vwsite2gfnFBU2"

print(f"Testing Company API Key (ending in {api_key[-8:]})...")

endpoints = [
    ("Company Profile", f"https://api.whop.com/api/v1/companies/{company_id}"),
    ("List Members (with company_id)", f"https://api.whop.com/api/v1/members?company_id={company_id}&first=10"),
    ("List Members (without param)", f"https://api.whop.com/api/v1/members?first=10"),
    ("List Memberships (with company_id)", f"https://api.whop.com/api/v1/memberships?company_id={company_id}&first=10"),
    ("List Memberships (without param)", f"https://api.whop.com/api/v1/memberships?first=10"),
    ("List Payments (with company_id)", f"https://api.whop.com/api/v1/payments?company_id={company_id}&first=10"),
    ("List Payments (without param)", f"https://api.whop.com/api/v1/payments?first=10"),
    ("List Invoices", f"https://api.whop.com/api/v1/invoices?company_id={company_id}&first=10"),
    ("List Users", f"https://api.whop.com/api/v1/users?company_id={company_id}&first=10"),
    ("Legacy Members v5 / api", f"https://api.whop.com/api/v5/members?company_id={company_id}"),
    ("V5 Memberships", f"https://api.whop.com/api/v5/memberships?company_id={company_id}"),
    ("V5 Payments", f"https://api.whop.com/api/v5/payments?company_id={company_id}")
]

for name, url in endpoints:
    print(f"\n==========================================")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Success! Response:")
            print(json.dumps(data, indent=2)[:1500])
        else:
            print(f"Error ({r.status_code}): {r.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")
