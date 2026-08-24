import os
import sys
import json
import requests
import re
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def extract_whop_public_profile(username: str):
    clean_user = username.lstrip("@")
    url = f"https://whop.com/@{clean_user}"
    
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return {"username": clean_user, "error": f"HTTP {r.status_code}"}
        
    html = r.text
    
    # 1. Earnings Badge
    earned_match = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned', html)
    raw_usd_match = re.search(r'totalEarningsWithTransfersInUsd:"([\d\.]+)"', html)
    
    # 2. Location string in header (e.g. "Shah Alam,MY", "New Caney,US", "Ashburn,US", "Prague,CZ", "Azusa,US")
    # In Whop HTML, location is rendered before "•Joined" or after "•"
    # Matches: [City/Region/State],[2-Letter Country Code]
    loc_match = re.search(r'([A-Za-z\u00C0-\u024F\s\.\-]+),\s*([A-Z]{2})\s*•\s*Joined', html)
    
    location_data = None
    if loc_match:
        city = loc_match.group(1).strip()
        country_code = loc_match.group(2).strip()
        # Clean any leading text if joined with handle
        if "@" in city:
            city = city.split("@")[-1].strip()
        if "Earned" in city:
            city = city.split("Earned")[-1].strip().lstrip("•").strip()
            
        location_data = {
            "city": city,
            "country_code": country_code,
            "display": f"{city}, {country_code}"
        }
        
    # 3. Joined Date
    joined_match = re.search(r'Joined\s+([A-Za-z]+\s+\d{4})', html)
    joined_date = joined_match.group(1) if joined_match else None
    
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
        "joined_date": joined_date,
        "location": location_data,
        "earnings": {
            "display_badge": earned_match.group(1) if earned_match else None,
            "exact_usd": float(raw_usd_match.group(1)) if raw_usd_match else None
        },
        "whop_partner": bool(user_meta.get("whop_partner_enabled_at")),
        "profile_url": url
    }

test_users = ["bonnielau", "dariuslewis32", "cameron", "jack", "moxyalili", "townhall", "scalewdreww"]

print("="*80)
print("TESTING PERFECTED PUBLIC PROFILE SCRAPER (LOCATION + EARNINGS)")
print("="*80)

for u in test_users:
    res = extract_whop_public_profile(u)
    print(f"\nUser: @{u}")
    print(json.dumps(res, indent=2))
