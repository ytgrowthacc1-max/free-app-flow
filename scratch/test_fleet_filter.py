import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from dashboard_server import _compute_fleet_summary_data

res = _compute_fleet_summary_data()
communities = res.get("communities", [])
summary = res.get("summary", {})

print("--- SUMMARY ---")
print(json.dumps(summary, indent=2))

# Test JS filtering simulation:
# Category: needs_attention, Visibility: visible_only
filtered_needs_att = [
    c for c in communities
    if not (c["is_hidden"] or c["is_suspended"])
    and (c["is_pinned"] and c["needs_attention"])
]

print(f"\nFiltered 'Needs Attention' + 'Visible Only': {len(filtered_needs_att)} communities")
for c in filtered_needs_att:
    print(f"  - Bot: {c['bot_handle']} | Comp: {c['company_name']} | Pinned: {c['is_pinned']} | Sched: {c['scheduler_enabled']} | Idle: {c['idle_minutes']}m | TokenValid: {c['token_valid']}")

# Test JS filtering simulation:
# Category: active_only, Visibility: visible_only
filtered_active = [
    c for c in communities
    if not (c["is_hidden"] or c["is_suspended"])
    and (c["is_pinned"] and c["scheduler_enabled"])
]
print(f"\nFiltered 'Active Schedulers' + 'Visible Only': {len(filtered_active)} communities")
for c in filtered_active:
    print(f"  - Bot: {c['bot_handle']} | Comp: {c['company_name']} | Pinned: {c['is_pinned']} | Sched: {c['scheduler_enabled']}")
