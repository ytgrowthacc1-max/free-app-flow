import requests
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def test_user_detail(u):
    r = requests.get(f"https://whop.com/@{u}", headers=headers)
    html = r.text
    
    country_m = re.search(r'\\?"country\\?"\s*:\s*\\?"([A-Za-z]{2})\\?"', html)
    # The actual city field in the RSC payload:
    # Look for ,"city":"Shah Alam" or \"city\":\"Shah Alam\"
    city_m = re.search(r'\\?"city\\?"\s*:\s*\\?"([A-Za-z\s\.\-]+?)\\?"', html)
    earned_m = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned', html)
    
    country = country_m.group(1) if country_m else None
    city = city_m.group(1) if (city_m and city_m.group(1) != "City") else None
    
    # Also check if city is in the header text: e.g. "Shah Alam,MY", "Prague,CZ"
    header_loc_m = re.search(r'([A-Za-z\u00C0-\u024F\s\.\-]+),\s*([A-Z]{2})\s*•\s*Joined', html)
    if header_loc_m:
        city = header_loc_m.group(1).split("Earned")[-1].lstrip("•").strip()
        country = header_loc_m.group(2).strip()
        
    print(f"@{u:15} | Country: {country or 'Not Set':7} | City: {city or 'Not Set':16} | Earned: {earned_m.group(1) if earned_m else '—'}")

for u in ["bonnielau", "dariuslewis32", "cameron", "jack", "moxyalili", "townhall", "scalewdreww"]:
    test_user_detail(u)
