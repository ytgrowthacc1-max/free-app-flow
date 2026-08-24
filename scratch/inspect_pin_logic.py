import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

print("--- SEARCH FOR PIN / PINNED / LOCALSTORAGE ---")
for i, line in enumerate(lines):
    if 'pin' in line.lower() or 'localstorage' in line.lower():
        print(f"Line {i+1}: {line}")
