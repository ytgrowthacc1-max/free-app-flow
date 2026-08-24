import psutil

pids = [28476, 23044]
for pid in pids:
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        print(f"Terminated PID {pid}")
    except Exception as e:
        print(f"Failed to terminate PID {pid}: {e}")
