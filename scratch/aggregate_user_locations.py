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

# Fetch all payments to extract all users with billing addresses
payments_url = f"https://api.whop.com/api/v1/payments?company_id={company_id}&first=100"
resp = requests.get(payments_url, headers=headers)

users_with_location = []
seen_users = set()

if resp.status_code == 200:
    payments = resp.json().get("data", [])
    for p in payments:
        user = p.get("user") or {}
        user_id = user.get("id")
        b_addr = p.get("billing_address")
        product = p.get("product") or {}
        
        entry = {
            "user_id": user_id,
            "username": user.get("username"),
            "name": user.get("name") or (b_addr.get("name") if b_addr else None),
            "email": user.get("email"),
            "product": product.get("title"),
            "amount": f"${p.get('total', 0):.2f}",
            "payment_status": p.get("status"),
            "payment_type": p.get("payment_method_type"),
            "date": p.get("created_at"),
            "location": None
        }
        
        if b_addr:
            entry["location"] = {
                "country": b_addr.get("country"),
                "state": b_addr.get("state"),
                "city": b_addr.get("city"),
                "postal_code": b_addr.get("postal_code"),
                "line1": b_addr.get("line1"),
                "line2": b_addr.get("line2")
            }
            
        if user_id not in seen_users:
            seen_users.add(user_id)
            users_with_location.append(entry)

print(f"Total Unique Users Analyzed from Payments: {len(users_with_location)}")
print(json.dumps(users_with_location, indent=2))
