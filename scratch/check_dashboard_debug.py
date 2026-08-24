import subprocess
import json

def check_ps():
    out = subprocess.check_output(['powershell', '-Command', 'Get-CimInstance Win32_Process | Select-Object ProcessId, CommandLine | ConvertTo-Json'], text=True)
    processes = json.loads(out)
    for p in processes:
        cmd = p.get('CommandLine') or ''
        if 'dashboard_server' in cmd or 'python' in cmd:
            print(f"PID: {p.get('ProcessId')}, CMD: {cmd}")

if __name__ == '__main__':
    check_ps()
