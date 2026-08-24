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

def extract_public_profile_earnings(username: str):
    clean_user = username.lstrip("@")
    url = f"https://whop.com/@{clean_user}"
    print(f"Scraping public profile for: @{clean_user} ({url})...")
    
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        print(f"Error fetching profile: {r.status_code}")
        return None
        
    html = r.text
    
    # Extract total earnings text (e.g. $2,719.35 Earned)
    earned_match = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*<!--\s*-->\s*<!--\s*-->\s*Earned', html)
    if not earned_match:
        earned_match = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*Earned', html)
    
    total_earned_display = earned_match.group(1) if earned_match else None
    
    # Extract exact total earnings from React RSC payload
    rsc_matches = re.findall(r'totalEarningsWithTransfersInUsd:"([\d\.]+)"', html)
    
    # Extract company breakdowns
    # Example: id:"biz_...",title:"...",totalEarningsWithTransfersInUsd:"..."
    company_blocks = re.findall(r'\{id:"(biz_[^"]+)",title:"([^"]+)",route:"([^"]+)",publishedReviewsCount:(\d+),reviewsAverage:([^,]+),totalEarningsWithTransfersInUsd:("[\d\.]+"|null)\}', html)
    
    # Extract public user profile fields from API
    user_api_url = f"https://api.whop.com/api/v1/users/{clean_user}"
    user_api_data = {}
    try:
        u_resp = requests.get(user_api_url, headers=headers, timeout=5)
        if u_resp.status_code == 200:
            user_api_data = u_resp.json()
    except Exception:
        pass
        
    return {
        "username": clean_user,
        "name": user_api_data.get("name"),
        "user_id": user_api_data.get("id"),
        "total_earned_display": total_earned_display,
        "total_earnings_usd": rsc_matches[0] if rsc_matches else None,
        "company_earnings": [
            {
                "company_id": c[0],
                "title": c[1],
                "slug": c[2],
                "reviews_count": int(c[3]),
                "reviews_average": float(c[4]) if c[4] != 'null' else None,
                "earnings_usd": float(c[5].replace('"', '')) if c[5] != 'null' else 0.0
            } for c in company_blocks
        ]
    }

# Test on @townhall
result = extract_public_profile_earnings("townhall")
print("\n" + "="*80)
print("EXTRACTED PUBLIC EARNINGS DOSSIER")
print("="*80)
print(json.dumps(result, indent=2))
