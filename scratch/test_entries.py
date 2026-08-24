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

urls = [
    f"https://api.whop.com/api/v1/entries?company_id={company_id}&member_id={member_id}",
    f"https://api.whop.com/api/v1/entries?company_id={company_id}&user_id={user_id}",
    f"https://api.whop.com/api/v1/entries?company_id={company_id}&first=5"
]

for u in urls:
    print(f"\n--- {u} ---")
    r = requests.get(u, headers=headers)
    print("Status:", r.status_code)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2)[:1000])
    else:
        print(r.text)
