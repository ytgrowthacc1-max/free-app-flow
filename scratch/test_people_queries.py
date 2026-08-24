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

# Test searching People API with email / user_id parameter
queries = [
    f"https://api.whop.com/api/v1/people?company_id={company_id}&email=detemele@gmail.com",
    f"https://api.whop.com/api/v1/people?company_id={company_id}&user_id=user_q0IOgsySDXOTr",
    f"https://api.whop.com/api/v1/people?company_id={company_id}&order=created_at_desc&first=20",
    f"https://api.whop.com/api/v1/people?company_id={company_id}&order=last_seen_at_desc&first=20"
]

for url in queries:
    print(f"\n--- URL: {url} ---")
    r = requests.get(url, headers=headers)
    print("Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        people = data.get("data", [])
        print(f"Count: {len(people)}")
        for p in people[:3]:
            print(f"  User: {p.get('user', {}).get('username')} | Email: {p.get('email')} | Location: {p.get('location')} | Timezone: {p.get('timezone')} | Last Seen: {p.get('last_seen_at')}")
    else:
        print(r.text)
