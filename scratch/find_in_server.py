with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "load_actions" in line or "save_actions" in line:
        print(f"Line {idx+1}: {line.strip()}")
