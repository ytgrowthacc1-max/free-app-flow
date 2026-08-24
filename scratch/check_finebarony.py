import os
import sys
import json
import requests

api_key = "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba"
company_id = "biz_Vwsite2gfnFBU2"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

user_id = "user_q0IOgsySDXOTr"
member_id = "mber_dOfr8ilPhAwHi"

print(f"Investigating user 'finebarony' ({user_id}, member: {member_id})...")

endpoints = [
    ("Member Details", f"https://api.whop.com/api/v1/members/{member_id}"),
    ("User Details", f"https://api.whop.com/api/v1/users/{user_id}"),
    ("Memberships by Member ID", f"https://api.whop.com/api/v1/memberships?member_id={member_id}"),
    ("Memberships by User ID", f"https://api.whop.com/api/v1/memberships?company_id={company_id}&user_id={user_id}"),
    ("Payments by User ID", f"https://api.whop.com/api/v1/payments?company_id={company_id}&user_id={user_id}"),
    ("Invoices by User ID", f"https://api.whop.com/api/v1/invoices?company_id={company_id}&user_id={user_id}"),
    ("Checkouts for Company", f"https://api.whop.com/api/v1/checkout_configurations?company_id={company_id}")
]

for name, url in endpoints:
    print(f"\n--- {name}: {url} ---")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")
