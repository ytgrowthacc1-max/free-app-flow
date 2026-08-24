with open(r"c:\Python\Health_APP_WHOP\app\page.tsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "mode" in line.lower() or "sqlite" in line.lower() or "dev" in line.lower():
        if "badge" in line or "header" in line or "sqlite" in line.lower():
            print(f"Line {i+1}: {line.strip()}")
