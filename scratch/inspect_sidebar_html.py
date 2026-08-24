import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

# Search for sidebar HTML lines
print("--- SIDEBAR HTML ---")
for i, line in enumerate(lines[:1000]): # first 1000 lines of HTML
    if 'profiles-tree' in line or 'sidebar' in line or 'filter-has-communities' in line or 'active-profile' in line:
        print(f"Line {i+1}: {line}")
