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

# 1. Fetch public profile page for @townhall
profile_urls = [
    "https://whop.com/@townhall",
    "https://whop.com/townhall",
    "https://api.whop.com/api/v1/users/townhall",
    "https://api.whop.com/api/v1/companies/townhall"
]

for url in profile_urls:
    print(f"\n--- Checking: {url} ---")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            if "application/json" in r.headers.get("content-type", ""):
                data = r.json()
                print("JSON Data:", json.dumps(data, indent=2)[:1500])
            else:
                # Look for __NEXT_DATA__ in HTML
                html = r.text
                print(f"HTML length: {len(html)}")
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
                if match:
                    next_data = json.loads(match.group(1))
                    print("Found __NEXT_DATA__!")
                    # Pretty print pageProps
                    page_props = next_data.get("props", {}).get("pageProps", {})
                    print("PageProps keys:", list(page_props.keys()))
                    print("PageProps content sample:", json.dumps(page_props, indent=2)[:2000])
                else:
                    # Search for numbers like 2720 or earnings in text
                    matches_2720 = re.findall(r'.{0,50}(?:2720|2,720|\$2|earnings|revenue).{0,50}', html, re.IGNORECASE)
                    print(f"Text matches for earnings/2720: {matches_2720[:5]}")
        else:
            print(f"Error ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
