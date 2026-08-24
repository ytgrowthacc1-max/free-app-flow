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

# Fetch the latest people ordered by first_seen_at / last_seen_at descending
url = f"https://api.whop.com/api/v1/people?company_id={company_id}&order=last_seen_at&direction=desc&first=50"
r = requests.get(url, headers=headers)
print("Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    people = data.get("data", [])
    print(f"Retrieved {len(people)} recent people.")
    for p in people[:15]:
        u = p.get("user") or {}
        print(f"User: @{u.get('username')} ({p.get('name')}) | Email: {p.get('email')} | Location: {p.get('location')} | Timezone: {p.get('timezone')} | Last Seen: {p.get('last_seen_at')}")
else:
    print(r.text)
