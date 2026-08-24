with open("execution/dashboard_server.py", "r", encoding="utf-8", errors="ignore") as f:
    for idx, line in enumerate(f, start=1):
        if "tab-btn" in line and "<button" in line:
            print(f"Line {idx}: {line.strip()}")
