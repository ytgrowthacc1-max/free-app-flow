with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = []
for i, line in enumerate(content.splitlines()):
    if "api.whop.com" in line or "requests.get" in line or "requests.post" in line or "requests.patch" in line:
        matches.append(f"Line {i+1}: {line.strip()}")

for m in matches[:50]:
    print(m)
