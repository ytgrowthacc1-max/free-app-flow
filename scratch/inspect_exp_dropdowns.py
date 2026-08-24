import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('execution/dashboard_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()

print("--- EXPERIENCES AND DROPDOWNS ---")
for i, line in enumerate(lines):
    if 'gen-experience-select' in line or 'detail-forum-select' in line or 'loadExperiences' in line or '/api/experiences' in line:
        print(f"Line {i+1}: {line}")
