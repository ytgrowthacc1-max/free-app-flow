with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [line for line in content.splitlines() if "_thread_local" in line]
for m in matches[:30]:
    print(m)
