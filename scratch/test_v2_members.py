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

endpoints = [
    f"https://api.whop.com/api/v2/members?company_id={company_id}",
    f"https://api.whop.com/api/v2/companies/{company_id}/members",
    f"https://api.whop.com/api/v5/companies/{company_id}/members",
    f"https://api.whop.com/api/v1/companies/{company_id}/members",
    f"https://whop.com/api/v2/members?company_id={company_id}",
    f"https://api.whop.com/api/v1/people?company_id={company_id}"
]

for url in endpoints:
    print(f"\nTesting: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("Response:", json.dumps(r.json(), indent=2)[:500])
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")
