with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for i, l in enumerate(lines):
    if 'def get_profiles():' in l:
        for j in range(i, min(i+90, len(lines))):
            print(f"Line {j+1}: {lines[j]}")
        break
