import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

print("--- SELECT ELEMENTS ---")
for i, line in enumerate(lines):
    if '<select' in line or 'select' in line and ('bot' in line or 'profile' in line) and ('<option' in line or 'id=' in line):
        print(f"Line {i+1}: {line}")

print("\n--- POPULATE SELECT FUNCTIONS ---")
for i, line in enumerate(lines):
    if 'populate' in line or 'fillSelect' in line or 'loadProfiles' in line or 'select' in line and ('option' in line or 'append' in line):
        if 'function' in line:
            print(f"Line {i+1}: {line}")
