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

url = f"https://api.whop.com/api/v1/people?company_id={company_id}&first=10"
r = requests.get(url, headers=headers)
print("Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    people = data.get("data", [])
    print(f"Retrieved {len(people)} people records.")
    for idx, p in enumerate(people[:3]):
        print(f"\n--- PERSON {idx+1} ---")
        print(json.dumps(p, indent=2))
        
    # Also check if we can query for finebarony in people
    url_finebarony = f"https://api.whop.com/api/v1/people?company_id={company_id}&query=finebarony"
    r2 = requests.get(url_finebarony, headers=headers)
    print("\n--- Search People for 'finebarony' ---")
    print("Status:", r2.status_code)
    if r2.status_code == 200:
        print(json.dumps(r2.json(), indent=2))
