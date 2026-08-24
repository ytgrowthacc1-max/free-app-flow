with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [line for line in content.splitlines() if "7331" in line or "PORT" in line or "port=" in line]
for m in matches[:20]:
    print(m)
