with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "post_to_forum" in line:
        print(f"Line {i+1}: {line.strip()}")
