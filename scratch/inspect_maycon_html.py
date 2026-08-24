import requests
import re
import sys

# Ensure UTF-8 printing
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

url = "https://whop.com/maycon-green-prediction-lair/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
resp = requests.get(url, headers=headers)
html = resp.text

whale_id = "prod_ZfObdbK29Tk2z"
matches = list(re.finditer(whale_id, html))

with open(".tmp/inspect_whale.txt", "w", encoding="utf-8") as f:
    f.write(f"Found {len(matches)} occurrences of {whale_id}\n")
    for i, m in enumerate(matches):
        start = max(0, m.start() - 150)
        end = min(len(html), m.end() + 1500)
        f.write(f"\n--- Occurrence {i} ---\n")
        f.write(html[start:end])
        f.write("\n")

print("Wrote inspect output to .tmp/inspect_whale.txt")
