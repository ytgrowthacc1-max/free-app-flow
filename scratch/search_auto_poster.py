with open('execution/auto_forum_poster.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if 'def ' in line or 'run_auto_poster' in line:
        safe_line = line.strip()[:120].encode('ascii', 'replace').decode('ascii')
        print(f"Line {idx+1}: {safe_line}")
