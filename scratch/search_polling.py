with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if 'forum_posts' in line or 'reactions' in line:
        if 'requests.get' in line or 'requests.post' in line or 'def ' in line:
            print(f"Line {idx+1}: {line.strip()[:120]}")
