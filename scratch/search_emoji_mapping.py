with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if 'emoji_mapping =' in line.lower() or 'emojimapping =' in line.lower():
        print(f"Line {idx+1}: {line.strip()[:120]}")
