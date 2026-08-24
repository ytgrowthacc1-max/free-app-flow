import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from dashboard_server import _compute_fleet_summary_data

res = _compute_fleet_summary_data()
communities = res.get("communities", [])

print(f"Total communities returned: {len(communities)}")
needs_att = [c for c in communities if c.get("needs_attention")]
print(f"Total communities with needs_attention=True: {len(needs_att)}")

for c in needs_att:
    print(f"- Bot: {c.get('bot_handle')} ({c.get('bot_user_id')}) | Comp: {c.get('company_name')} ({c.get('company_id')}) | Pinned: {c.get('is_pinned')} | Sched: {c.get('scheduler_enabled')} | TokenValid: {c.get('token_valid')} | Idle: {c.get('idle_minutes')}m | Hidden: {c.get('is_hidden')} | Suspended: {c.get('is_suspended')}")
