import json
import os

pfile = ".tmp/pending_actions.json"
if os.path.exists(pfile):
    with open(pfile, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    forum_actions = [a for a in data if a.get("type") == "forum"]
    print("Forum action count:", len(forum_actions))
    for i, a in enumerate(forum_actions):
        print(f"Action {i}: ID={a.get('id')}, Status={a.get('status')}, Company={a.get('company_id')}, Title='{a.get('title', '')[:50]}...'")
        print("  Keys:", list(a.keys()))
        print("  Content preview:", a.get("content", "")[:100])
        print("-" * 30)
else:
    print("Pending file does not exist.")
