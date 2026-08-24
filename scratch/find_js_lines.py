with open("execution/dashboard_server.py", "r", encoding="utf-8", errors="ignore") as f:
    for idx, line in enumerate(f, start=1):
        if "function switchFilter" in line or "function selectCampaignPreset" in line:
            print(f"Line {idx}: {line.strip()}")
