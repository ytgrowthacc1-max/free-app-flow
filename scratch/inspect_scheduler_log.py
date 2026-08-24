import os

log_file = ".tmp/scheduler.log"
if os.path.exists(log_file):
    print(f"Log size: {os.path.getsize(log_file)} bytes")
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        for line in lines[-100:]:
            print(line.strip())
    except Exception as e:
        print("Error reading log:", e)
else:
    print("Log file does not exist.")
