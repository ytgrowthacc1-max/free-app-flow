import os
import sys
import json
import requests

api_key = "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba"
company_id = "biz_Vwsite2gfnFBU2"
user_id = "user_q0IOgsySDXOTr"
member_id = "mber_dOfr8ilPhAwHi"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

probes = [
    f"https://api.whop.com/api/v1/members/{member_id}",
    f"https://api.whop.com/api/v1/members/{member_id}/activity",
    f"https://api.whop.com/api/v1/members/{member_id}/devices",
    f"https://api.whop.com/api/v1/entries?member_id={member_id}",
    f"https://api.whop.com/api/v1/entries?user_id={user_id}",
    f"https://api.whop.com/api/v1/users/{user_id}/profile",
    f"https://api.whop.com/api/v1/checkout_sessions?user_id={user_id}",
    f"https://api.whop.com/api/v1/checkout_sessions?company_id={company_id}",
    f"https://api.whop.com/api/v1/companies/{company_id}/exports"
]

for url in probes:
    print(f"\nProbing: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("Response:", json.dumps(r.json(), indent=2)[:500])
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")
