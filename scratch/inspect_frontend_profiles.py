with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

# Search for fetches of /api/profiles or loadProfiles or renderProfiles or select profile element IDs
for i, line in enumerate(lines):
    if '/api/profiles' in line or 'loadProfiles' in line or 'renderProfiles' in line or 'profile-select' in line or 'profileSelect' in line or 'populateProfiles' in line:
        print(f"Line {i+1}: {line}")
