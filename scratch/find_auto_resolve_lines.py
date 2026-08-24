with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "def auto_resolve_active_profile" in line:
        print(f"Start: line {i+1}")
        # Find the next def or end of function
        for j in range(i+1, len(lines)):
            if lines[j].startswith("def ") or lines[j].startswith("@app."):
                print(f"End: line {j+1}")
                break
        break
