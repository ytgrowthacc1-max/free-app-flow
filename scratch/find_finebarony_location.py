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

target_username = "finebarony"
target_user_id = "user_q0IOgsySDXOTr"
target_email = "detemele@gmail.com"

print(f"Searching for {target_username} in People API...")

has_next = True
cursor = ""
page = 1
found_person = None
all_people_sample = []

while has_next and page <= 20:
    url = f"https://api.whop.com/api/v1/people?company_id={company_id}&first=50"
    if cursor:
        url += f"&after={cursor}"
        
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error on page {page}: {r.status_code} - {r.text}")
        break
        
    data = r.json()
    people = data.get("data", [])
    
    for p in people:
        user = p.get("user") or {}
        p_email = p.get("email")
        p_username = user.get("username")
        p_user_id = user.get("id")
        
        all_people_sample.append({
            "username": p_username,
            "email": p_email,
            "location": p.get("location"),
            "timezone": p.get("timezone"),
            "device": p.get("device"),
            "last_seen_at": p.get("last_seen_at")
        })
        
        if (p_username and p_username.lower() == target_username.lower()) or \
           (p_user_id == target_user_id) or \
           (p_email and p_email.lower() == target_email.lower()):
            found_person = p
            break
            
    if found_person:
        break
        
    page_info = data.get("page_info", {})
    has_next = page_info.get("has_next_page", False)
    cursor = page_info.get("end_cursor")
    page += 1

print("\n" + "="*80)
if found_person:
    print(f"🎉 FOUND {target_username.upper()} IN PEOPLE API!")
    print("="*80)
    print(json.dumps(found_person, indent=2))
else:
    print(f"Not found in first {len(all_people_sample)} people records. Showing sample of other free members:")
    print("="*80)
    for p in all_people_sample[:10]:
        print(f"User: @{p['username']} | Email: {p['email']} | Location: {p['location']} | Timezone: {p['timezone']} | Device: {p['device']}")
