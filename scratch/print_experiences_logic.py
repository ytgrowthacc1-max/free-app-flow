import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

print("--- JS FETCH EXPERIENCES (lines 4830-4880) ---")
for i in range(4829, 4880):
    if i < len(lines):
        print(f"Line {i+1}: {lines[i]}")

print("\n--- PYTHON ROUTE EXPERIENCES (lines 8062-8135) ---")
for i in range(8061, 8135):
    if i < len(lines):
        print(f"Line {i+1}: {lines[i]}")
