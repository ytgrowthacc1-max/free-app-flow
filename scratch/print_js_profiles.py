import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

print("--- LINES 3560-3600 ---")
for i in range(3559, 3600):
    if i < len(lines):
        print(f"Line {i+1}: {lines[i]}")

print("\n--- LINES 5150-5250 ---")
for i in range(5149, 5250):
    if i < len(lines):
        print(f"Line {i+1}: {lines[i]}")
