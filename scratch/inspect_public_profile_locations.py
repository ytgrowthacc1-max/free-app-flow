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

sample_users = [
    "townhall",
    "scalewdreww",
    "therealr1cky",
    "bonnielau",
    "dariuslewis32",
    "cameron",
    "steven",
    "jack",
    "adam",
    "moxyalili"
]

print("--- INSPECTING PUBLIC PROFILES FOR LOCATION DATA ---")

for username in sample_users:
    url = f"https://whop.com/@{username}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"\nUser @{username}: HTTP {r.status_code}")
            continue
            
        html = r.text
        
        # 1. Search for location keywords, country codes, SVG flag icons, or location pin icons in HTML
        # In Whop profile UI, location might be rendered near bio or header with a pin icon or country name
        # Let's search for patterns
        
        # Look for country patterns or location badges
        loc_patterns = re.findall(r'(\b[A-Za-z\s,]+(?:United States|USA|UK|United Kingdom|Germany|Spain|Canada|France|Australia|India|Philippines|Morocco|Nigeria|Brazil|Mexico|Dubai|UAE|Singapore|Japan|Italy|Netherlands)\b)', html, re.IGNORECASE)
        
        # Look for JSON keys like "location", "country", "city", "state", "countryCode"
        json_loc_matches = re.findall(r'"(?:location|country|city|countryCode|country_code|state)"\s*:\s*("[^"]+"|\{[^}]+\})', html)
        
        # Look for svg icons or text near user header
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all text snippets in the profile header / about card
        text_snippets = []
        for el in soup.find_all(["span", "p", "div"], class_=True):
            cls = " ".join(el.get("class", []))
            txt = el.get_text(strip=True)
            if txt and len(txt) < 80:
                # Filter interesting snippets
                if any(k in txt.lower() for k in ["earned", "member", "joined", "location", "from", "📍", "🇺🇸", "🇬🇧", "🇩🇪", "🇨🇦", "🇦🇺", "🇪🇸", "🇫🇷", "🇮🇳"]):
                    text_snippets.append(txt)
                    
        # Check if there are country flag emojis
        flag_emojis = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', html)
        
        print(f"\n==================================================")
        print(f"USER: @{username}")
        print(f"URL: {url}")
        print(f"Flag emojis found: {set(flag_emojis)}")
        print(f"Header text snippets: {text_snippets[:8]}")
        print(f"JSON location matches: {json_loc_matches[:5]}")
        
    except Exception as e:
        print(f"Error on @{username}: {e}")
