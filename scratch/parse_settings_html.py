with open(".tmp/settings_page.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Find img tags or profile containers
for m in re.finditer(r'<img[^>]+>', content):
    print("IMG:", m.group(0)[:150])

print("\n--- Search for dawnmuros ---")
idx = content.find("dawnmuros")
if idx != -1:
    print(content[max(0, idx-300):min(len(content), idx+500)])
