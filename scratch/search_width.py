with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if 'width:' in line.lower() and ('px' in line.lower() or 'vw' in line.lower() or '%' in line.lower()):
        # Print only stylesheet lines (lines < 1184)
        if idx + 1 < 1184:
            print(f"Line {idx+1}: {line.strip()[:120]}")
