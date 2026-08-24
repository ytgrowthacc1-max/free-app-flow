import glob
import json

files = glob.glob(".tmp/pending_actions_*.json")
print(f"Found {len(files)} pending_actions files:")

for fn in files:
    try:
        with open(fn, "r", encoding="utf-8") as f:
            items = json.load(f)
        if items:
            print(f"\nFile: {fn} ({len(items)} items)")
            for item in items:
                print(f"  - ID: {item.get('id')} | Status: {item.get('status')} | Title/Text: {str(item.get('title') or item.get('content') or item.get('post_title'))[:50]}")
    except Exception as e:
        print(f"Error reading {fn}: {e}")
