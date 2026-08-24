with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for i in range(len(lines)-30, len(lines)):
    print(f"Line {i+1}: {lines[i]}")
