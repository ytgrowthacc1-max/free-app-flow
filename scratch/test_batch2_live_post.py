import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from post_to_forum import post_to_forum
from whop_auth import get_fresh_token

# Test Bot 11: @stanleyrodrigueze2 (App Builders VIP)
bot_id = "user_7TW5tuOsmnpOq"
master_cid = "biz_NVxgoFpMbXPl6u"
master_exp = "exp_HtI6xOMgG3go4J"

sched_path = os.path.join(BASE_DIR, "profiles", "bots", bot_id, master_cid, "scheduler_settings.json")
sdata = json.load(open(sched_path, encoding="utf-8"))
reshare_targets = sdata.get("reshare_experience_ids", [])

print(f"Testing live Master Poll & Cross-Reshares on @stanleyrodrigueze2 ({len(reshare_targets)} targets)...")

test_title = "Which micro SaaS engine will generate your first $1,000 MRR?"
test_content = "Vote below and share your stack in the comments!"
poll_payload = {
    "options": [
        {"id": "1", "text": "AI Workflow Automation"},
        {"id": "2", "text": "B2B Chrome Extensions"},
        {"id": "3", "text": "NoCode Directory Builder"},
        {"id": "4", "text": "Micro Analytics Tool"}
    ]
}

print(f"[TEST 1/2] Posting Master Poll to {master_exp}...")
master_post = post_to_forum(
    experience_id=master_exp,
    content=test_content,
    title=test_title,
    pinned=False,
    is_mention=False,
    visibility="members_only",
    poll=poll_payload,
    bot_user_id=bot_id
)

if not master_post or not master_post.get("id"):
    print(f"[ERROR] Failed to post: {master_post}")
    sys.exit(1)

master_post_id = master_post.get("id")
print(f"  [SUCCESS] Master Post ID: {master_post_id}")

print(f"[TEST 2/2] Broadcasting reshare to all {len(reshare_targets)} secondary communities...")
success_count = 0
for idx, t_exp in enumerate(reshare_targets, 1):
    time.sleep(0.3)
    res_post = post_to_forum(
        experience_id=t_exp,
        content=test_content,
        title=test_title,
        pinned=False,
        is_mention=False,
        visibility="members_only",
        poll=poll_payload,
        bot_user_id=bot_id
    )
    if res_post and res_post.get("id"):
        success_count += 1
    else:
        print(f"    [FAIL] Target {idx} ({t_exp}) failed: {res_post}")

print(f"\n[FINAL RESULT] Reshared {success_count}/{len(reshare_targets)} successfully!")
if success_count == len(reshare_targets):
    print("[100% OPERATIONAL PASS] Full master-to-secondaries cross-posting confirmed!")
