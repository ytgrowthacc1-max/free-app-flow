import os

log_file = ".tmp/scheduler.log"
if os.path.exists(log_file):
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print("Lines for @ericdavis8b:")
        count = 0
        for line in lines:
            if "@ericdavis8b" in line:
                print(line.strip())
                count += 1
        print(f"Total occurrences: {count}")
    except Exception as e:
        print("Error reading log:", e)
else:
    print("Log file does not exist.")
