import os

desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
bat_path = os.path.join(desktop_path, 'Whop Automation Controller.bat')

bat_content = """@echo off
cd /d "c:\\Python\\WHOP AUTOMATION AGENTIC"
start "" pythonw execution\\whop_automation_control.py
exit
"""

with open(bat_path, 'w', encoding='utf-8') as f:
    f.write(bat_content)

print(f"[SUCCESS] Created desktop launcher at: {bat_path}")
