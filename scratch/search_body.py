with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
found = False
for idx, line in enumerate(lines):
    if '<body' in line or 'class="main-layout"' in line:
        found = True
        print(f"Line {idx+1}: {line.strip()[:120]}")
