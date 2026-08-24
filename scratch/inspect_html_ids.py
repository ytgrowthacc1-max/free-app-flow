import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

for i in range(348, 3500):
    l = lines[i]
    if 'profiles-tree' in l or 'profiles' in l and ('id=' in l or 'class=' in l):
        print(f"Line {i+1}: {l}")
