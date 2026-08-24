import glob
import json
import os

pending_files = glob.glob(".tmp/pending_actions_*.json")

total_fixed = 0
files_modified = 0

for pfile in pending_files:
    try:
        with open(pfile, "r", encoding="utf-8") as f:
            actions = json.load(f)
    except Exception:
        continue
    
    modified = False
    for a in actions:
        # If an action has a post_id or published_at or status is approved with post_id
        if a.get("post_id") or a.get("published_at"):
            if a.get("status") != "published":
                a["status"] = "published"
                modified = True
                total_fixed += 1
                
    if modified:
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(actions, f, indent=2)
        files_modified += 1

print(f"DONE! Fixed {total_fixed} actions across {files_modified} files to 'published'.")
