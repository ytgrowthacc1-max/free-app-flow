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

print("="*80)
print("PULLING MEMBERS DATA FOR APP BUILDERS")
print("="*80)

# 1. Fetch Members
members_resp = requests.get(f"https://api.whop.com/api/v1/members?company_id={company_id}&first=50", headers=headers)
if members_resp.status_code == 200:
    members_data = members_resp.json().get("data", [])
    print(f"Retrieved {len(members_data)} members.")
    print("\n--- SAMPLE MEMBER OBJECT ---")
    if members_data:
        print(json.dumps(members_data[0], indent=2))
        
        # Also test individual GET /members/{id}
        first_member_id = members_data[0].get("id")
        m_detail_resp = requests.get(f"https://api.whop.com/api/v1/members/{first_member_id}", headers=headers)
        print(f"\n--- GET /members/{first_member_id} Status: {m_detail_resp.status_code} ---")
        if m_detail_resp.status_code == 200:
            print(json.dumps(m_detail_resp.json(), indent=2))
else:
    print(f"Error fetching members: {members_resp.status_code} - {members_resp.text}")

print("\n" + "="*80)
print("PULLING MEMBERSHIPS DATA")
print("="*80)

# 2. Fetch Memberships
memberships_resp = requests.get(f"https://api.whop.com/api/v1/memberships?company_id={company_id}&first=50", headers=headers)
if memberships_resp.status_code == 200:
    memberships_data = memberships_resp.json().get("data", [])
    print(f"Retrieved {len(memberships_data)} memberships.")
    if memberships_data:
        print("\n--- SAMPLE MEMBERSHIP OBJECT ---")
        print(json.dumps(memberships_data[0], indent=2))
        
        # Test individual membership
        first_mem_id = memberships_data[0].get("id")
        mem_detail_resp = requests.get(f"https://api.whop.com/api/v1/memberships/{first_mem_id}", headers=headers)
        print(f"\n--- GET /memberships/{first_mem_id} Status: {mem_detail_resp.status_code} ---")
        if mem_detail_resp.status_code == 200:
            print(json.dumps(mem_detail_resp.json(), indent=2))
else:
    print(f"Error fetching memberships: {memberships_resp.status_code} - {memberships_resp.text}")

print("\n" + "="*80)
print("PULLING PAYMENTS DATA")
print("="*80)

# 3. Fetch Payments
payments_resp = requests.get(f"https://api.whop.com/api/v1/payments?company_id={company_id}&first=50", headers=headers)
if payments_resp.status_code == 200:
    payments_data = payments_resp.json().get("data", [])
    print(f"Retrieved {len(payments_data)} payments.")
    for idx, p in enumerate(payments_data[:5]):
        print(f"\n--- PAYMENT {idx+1} ---")
        print(json.dumps(p, indent=2))
        
        pay_id = p.get("id")
        p_detail = requests.get(f"https://api.whop.com/api/v1/payments/{pay_id}", headers=headers)
        print(f"Detail for {pay_id}: Status {p_detail.status_code}")
        if p_detail.status_code == 200:
            print(json.dumps(p_detail.json(), indent=2))
else:
    print(f"Error fetching payments: {payments_resp.status_code} - {payments_resp.text}")
