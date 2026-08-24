import os
import sys
import json
import requests
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def extract_whop_profile_all_public_data(username: str):
    clean_user = username.lstrip("@")
    url = f"https://whop.com/@{clean_user}"
    
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return {"username": clean_user, "error": f"HTTP {r.status_code}"}
        
    html = r.text
    
    # 1. Extract Exact Country & City from RSC JSON Payload
    country_match = re.search(r'\\"country\\":\s*\\"([A-Z]{2})\\"', html)
    city_match = re.search(r'\\"city\\":\s*\\"([^\\"]+)\\"', html)
    
    # 2. Extract Last Seen timestamp
    last_seen_match = re.search(r'\\"lastSeenAt\\":\s*(\d+)', html)
    
    # 3. Extract Earnings Badge & Raw USD
    earned_badge = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned', html)
    raw_usd_match = re.search(r'totalEarningsWithTransfersInUsd:"([\d\.]+)"', html)
    
    # 4. User API Metadata
    user_api_url = f"https://api.whop.com/api/v1/users/{clean_user}"
    user_meta = {}
    try:
        u_resp = requests.get(user_api_url, headers=headers, timeout=5)
        if u_resp.status_code == 200:
            user_meta = u_resp.json()
    except Exception:
        pass
        
    return {
        "username": clean_user,
        "name": user_meta.get("name"),
        "user_id": user_meta.get("id"),
        "bio": user_meta.get("bio"),
        "location": {
            "country": country_match.group(1) if country_match else None,
            "city": city_match.group(1) if city_match else None,
            "display": f"{city_match.group(1)}, {country_match.group(1)}" if (city_match and country_match) else (country_match.group(1) if country_match else None)
        },
        "earnings": {
            "display_badge": earned_badge.group(1) if earned_badge else None,
            "exact_usd": float(raw_usd_match.group(1)) if raw_usd_match else None
        },
        "last_seen_epoch": int(last_seen_match.group(1)) if last_seen_match else None,
        "whop_partner": bool(user_meta.get("whop_partner_enabled_at")),
        "profile_url": url
    }

test_users = [
    "townhall",
    "bonnielau",
    "dariuslewis32",
    "cameron",
    "jack",
    "moxyalili",
    "scalewdreww",
    "therealr1cky"
]

print("="*80)
print("TESTING PUBLIC LOCATION & EARNINGS EXTRACTOR ACROSS MULTIPLE USERS")
print("="*80)

for u in test_users:
    res = extract_whop_profile_all_public_data(u)
    print(f"\nUser: @{u}")
    print(json.dumps(res, indent=2))
