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

r = requests.get("https://whop.com/@townhall", headers=headers)
html = r.text

# Let's find all company objects and earnings in the HTML
matches = re.findall(r'id:"(biz_[^"]+)",title:"([^"]+)",route:"([^"]+)"[^}]*?totalEarningsWithTransfersInUsd:("[\d\.]+"|null)', html)
print(f"Found {len(matches)} company entries:")
for m in matches:
    print(f"  Company: {m[1]} ({m[0]}) | Route: whop.com/{m[2]} | Earnings: {m[3]}")

# Also let's extract all numbers/badges
earned_badge = re.findall(r'\$[\d,]+(?:\.\d+)?\s*(?:<!--\s*-->\s*)*Earned', html)
print(f"Earned Badge Text: {earned_badge}")
