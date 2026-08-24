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

def get_whop_creator_public_earnings(username: str):
    clean_user = username.lstrip("@")
    url = f"https://whop.com/@{clean_user}"
    
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return {"username": clean_user, "error": f"HTTP {r.status_code}"}
        
    html = r.text
    
    # 1. Regex for Earned Badge text
    earned_badge = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned', html)
    
    # 2. Regex for exact raw USD value in RSC payload
    raw_usd = re.search(r'totalEarningsWithTransfersInUsd:"([\d\.]+)"', html)
    
    # 3. User metadata
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
        "created_at": user_meta.get("created_at"),
        "public_earnings_badge": earned_badge.group(1) if earned_badge else "Not displayed",
        "exact_earnings_usd": float(raw_usd.group(1)) if raw_usd else None,
        "whop_partner": bool(user_meta.get("whop_partner_enabled_at")),
        "profile_url": url
    }

test_creators = ["townhall", "scalewdreww", "therealr1cky"]
for c in test_creators:
    res = get_whop_creator_public_earnings(c)
    print("\n" + "="*60)
    print(f"CREATOR EARNINGS PROFILE: @{c}")
    print("="*60)
    print(json.dumps(res, indent=2))
