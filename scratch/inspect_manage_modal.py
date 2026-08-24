import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

for i, l in enumerate(lines):
    if 'openManageCommunitiesModal' in l or 'renderManageCommunities' in l:
        print(f"Line {i+1}: {l}")
