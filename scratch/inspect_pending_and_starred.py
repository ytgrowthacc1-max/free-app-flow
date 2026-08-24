import glob
import json
import os

print("=== CHECKING PENDING ACTIONS IN ALL COMMUNITIES ===")
pending_files = glob.glob(".tmp/pending_actions_*.json")

summary = {}
for pfile in pending_files:
    company_id = os.path.basename(pfile).replace("pending_actions_", "").replace(".json", "")
    try:
        with open(pfile, "r", encoding="utf-8") as f:
            actions = json.load(f)
    except Exception:
        continue
    
    statuses = {}
    for a in actions:
        st = a.get("status", "unknown")
        statuses[st] = statuses.get(st, 0) + 1
    
    # Check if there are non-published posts
    non_pub = [a for a in actions if a.get("status") in ["pending", "approved", "scheduled"]]
    if non_pub:
        summary[company_id] = {
            "total": len(actions),
            "breakdown": statuses,
            "sample_non_pub": [{"id": a.get("id"), "status": a.get("status"), "post_id": a.get("post_id"), "created_at": a.get("created_at"), "scheduled_time": a.get("scheduled_time")} for a in non_pub[:3]]
        }

print(f"Found {len(summary)} companies with non-published pending/approved/scheduled posts:")
for cid, info in summary.items():
    print(f"Company ID {cid}: {info['breakdown']} (Total: {info['total']})")
    for s in info['sample_non_pub']:
        print(f"  - Action {s['id']}: status={s['status']}, post_id={s['post_id']}, created={s['created_at']}, sched={s['scheduled_time']}")
