with open(".tmp/scheduler.log", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
for line in lines[-50:]:
    print(line.strip())
