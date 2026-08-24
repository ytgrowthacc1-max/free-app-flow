import requests

url = "https://whop.com/posts/post_1CcWJ19CqHpg4Z4ksFVyk4"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
r = requests.get(url, headers=headers)
html = r.text

print("Length of HTML:", len(html))
print("Contains 'post_1CcWJ19CqHpg4Z4ksFVyk4':", "post_1CcWJ19CqHpg4Z4ksFVyk4" in html)

# Search for parts of the title
title_parts = ["How", "much", "made", "Whop", "so far"]
for part in title_parts:
    print(f"Contains '{part}':", part in html or part.lower() in html.lower())

# Let's dump matches for 'poll'
import re
matches = [m.start() for m in re.finditer('poll', html, re.IGNORECASE)]
print(f"Found {len(matches)} matches for 'poll'.")
for idx, pos in enumerate(matches[:5]):
    print(f"Match {idx+1}: {html[max(0, pos-50):pos+100]!r}")
