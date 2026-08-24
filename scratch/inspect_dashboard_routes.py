with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
print("Total lines:", len(lines))

# Search for route definitions
print("\n--- ROUTES FOUND ---")
for idx, line in enumerate(lines):
    if '@app.route' in line:
        print(f"Line {idx+1}: {line}")
        # print next 2 lines
        for j in range(1, 4):
            if idx+j < len(lines):
                print(f"  + {lines[idx+j]}")

# Search for profile selection logic in JS or python
print("\n--- PROFILE LOGIC SEARCH ---")
for idx, line in enumerate(lines):
    if 'get_profiles' in line or '/api/profiles' in line or 'select_profile' in line or 'bot_user_id' in line and ('route' in line or 'function' in line or 'def ' in line):
        print(f"Line {idx+1}: {line[:100]}")
