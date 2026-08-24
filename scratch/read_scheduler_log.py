import os

log_file = ".tmp/scheduler.log"
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        print(f"Total log lines: {len(lines)}")
        print("--- LAST 60 LINES ---")
        for l in lines[-60:]:
            print(l.strip())
else:
    print("No .tmp/scheduler.log found!")
