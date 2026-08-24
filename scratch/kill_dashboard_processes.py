import subprocess
import json
import time

def kill_dashboard_processes():
    out = subprocess.check_output(['powershell', '-Command', 'Get-CimInstance Win32_Process | Select-Object ProcessId, CommandLine | ConvertTo-Json'], text=True)
    processes = json.loads(out)
    killed = 0
    for p in processes:
        cmd = p.get('CommandLine') or ''
        pid = p.get('ProcessId')
        if 'dashboard_server.py' in cmd:
            print(f"Killing process PID {pid}: {cmd}")
            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            killed += 1
    print(f"Killed {killed} dashboard process(es).")

if __name__ == '__main__':
    kill_dashboard_processes()
