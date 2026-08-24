import os

paths_to_search = [
    r"c:\Python\WHOP AUTOMATION AGENTIC",
    r"c:\Python\Browsing Skill Agent",
    r"C:\Users\Eridas\.gemini\antigravity"
]

print("Searching for scheduler.log:")
for base in paths_to_search:
    if not os.path.exists(base):
        continue
    for root, dirs, files in os.walk(base):
        if "node_modules" in root or ".git" in root:
            continue
        for file in files:
            if file == "scheduler.log":
                path = os.path.join(root, file)
                print(f"Found: {path} ({os.path.getsize(path)} bytes)")
