import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

marie_dir = None
for bot_id in os.listdir(bots_dir):
    pfile = os.path.join(bots_dir, bot_id, "profile.json")
    if os.path.exists(pfile):
        with open(pfile, "r", encoding="utf-8") as f:
            pdata = json.load(f)
        if pdata.get("bot_username") == "mariesorensen":
            marie_dir = os.path.join(bots_dir, bot_id)
            print(f"Found @mariesorensen directory: {marie_dir}")
            break

if marie_dir:
    for root, dirs, files in os.walk(marie_dir):
        for file in files:
            path = os.path.join(root, file)
            rel = os.path.relpath(path, marie_dir)
            print(f"File: {rel}")
            if file.endswith(".json") or file.endswith(".txt") or file.endswith(".md"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    print(f"--- Content of {rel} ---")
                    if len(content) > 500:
                        print(content[:500] + "\n... (truncated)")
                    else:
                        print(content)
                    print("-" * 30)
                except Exception as e:
                    print(f"Error reading file: {e}")
else:
    print("Could not find @mariesorensen profile.")
