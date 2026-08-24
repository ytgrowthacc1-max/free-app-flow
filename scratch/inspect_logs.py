import os

log_path = ".tmp/scheduler.log"
if os.path.exists(log_path):
    print("Searching for specific publication/error events for @appdevelopment...")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        matches = []
        for line in f:
            if "@appdevelopment" in line:
                if any(x in line for x in ["published", "Queued post", "AUTOPILOT", "ERROR", "WARNING", "Failed", "Voted", "Liked", "Commented"]):
                    if "proceeding" not in line and "cooldown" not in line:
                        matches.append(line.strip())
        print(f"Found {len(matches)} matching entries:")
        for m in matches[-50:]:
            print(m)
else:
    print("Log file does not exist.")
