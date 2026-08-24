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

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def test_extract(username):
    url = f"https://whop.com/@{username}"
    r = requests.get(url, headers=headers)
    html = r.text
    
    # 1. Regex for country & city in JSON payload
    country_m = re.search(r'"country"\s*:\s*"([A-Z]{2})"', html)
    city_m = re.search(r'"city"\s*:\s*"([^"]+)"', html)
    
    # 2. Earnings
    earned_badge = re.search(r'(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned', html)
    
    country = country_m.group(1) if country_m else None
    city = city_m.group(1) if city_m else None
    
    print(f"@{username:15} | Country: {country or '—':3} | City: {city or '—':15} | Earned: {earned_badge.group(1) if earned_badge else '—'}")

users = ["townhall", "bonnielau", "dariuslewis32", "cameron", "jack", "moxyalili", "scalewdreww", "therealr1cky", "adam", "steven"]

print("="*75)
print("TESTING DIRECT REGEX PARSING OF PUBLIC PROFILES")
print("="*75)
for u in users:
    test_extract(u)
