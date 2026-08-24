with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "@app.route" in line or "@server.route" in line or "def get_pending" in line or "def get_actions" in line:
        print(f"Line {idx+1}: {line.strip()}")
