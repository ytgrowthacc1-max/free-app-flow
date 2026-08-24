import os
import glob
import json

files = glob.glob(".tmp/pending_actions_*.json")
print(f"Inspecting {len(files)} pending_actions files...")

fixed_count = 0

for fn in files:
    try:
        with open(fn, "r", encoding="utf-8") as f:
            items = json.load(f)
        
        modified = False
        for item in items:
            # If item has post_id, it has already been published to Whop!
            if item.get("post_id") and item.get("status") in ["approved", "scheduled", "pending"]:
                print(f"File {fn}: Item {item.get('id')} has post_id={item.get('post_id')} but status={item.get('status')}. Updating status -> 'published'.")
                item["status"] = "published"
                modified = True
                fixed_count += 1
                
        if modified:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
    except Exception as e:
        print(f"Error reading {fn}: {e}")

print(f"\nTotal already-published items updated to status='published': {fixed_count}")
