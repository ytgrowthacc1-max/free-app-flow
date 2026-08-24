import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

print("\n--- LINES 5250-5320 ---")
for i in range(5249, 5320):
    if i < len(lines):
        print(f"Line {i+1}: {lines[i]}")
