import requests
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def test_user(u):
    r = requests.get(f"https://whop.com/@{u}", headers=headers)
    html = r.text
    
    # Match escaped or unescaped country / city
    country_m = re.search(r'\\?"country\\?"\s*:\s*\\?"([A-Za-z]{2})\\?"', html)
    city_m = re.search(r'\\?"city\\?"\s*:\s*\\?"([^\\"]+)\\?"', html)
    earned_m = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned', html)
    
    country = country_m.group(1) if country_m else None
    city = city_m.group(1) if city_m else None
    earned = earned_m.group(1) if earned_m else None
    
    print(f"@{u:15} -> Country: {country or 'Not Set':5} | City: {city or 'Not Set':20} | Earned: {earned or '—'}")

test_list = ["bonnielau", "dariuslewis32", "cameron", "jack", "moxyalili", "townhall", "scalewdreww", "therealr1cky"]
for u in test_list:
    test_user(u)
