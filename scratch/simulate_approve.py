import os
import sys
import json

sys.path.append(os.path.abspath("execution"))
from post_to_forum import post_to_forum
from whop_auth import get_fresh_token

# Let's find a pending action for App Builders
pfile = ".tmp/pending_actions.json"
if not os.path.exists(pfile):
    print("Pending actions file not found.")
    exit()

with open(pfile, "r", encoding="utf-8") as f:
    actions = json.load(f)

app_builder_actions = [a for a in actions if a.get("type") == "forum" and a.get("status") == "pending" and a.get("company_id") == "biz_Vwsite2gfnFBU2"]
print(f"Found {len(app_builder_actions)} pending actions for App Builders.")

if not app_builder_actions:
    # Check community specific file
    comp_file = ".tmp/pending_actions_biz_Vwsite2gfnFBU2.json"
    if os.path.exists(comp_file):
        with open(comp_file, "r", encoding="utf-8") as f:
            app_builder_actions = json.load(f)
        app_builder_actions = [a for a in app_builder_actions if a.get("type") == "forum" and a.get("status") == "pending"]
        print(f"Found {len(app_builder_actions)} pending actions in company-specific file.")

if not app_builder_actions:
    print("No pending forum actions found for App Builders.")
    exit()

action = app_builder_actions[0]
print(f"\nSimulating approval for Action ID: {action['id']}")
print(f"Title: {action.get('title')}")
print(f"Experience ID: {action.get('experience_id')}")

# Setup environment to use appdevelopment bot profile (user_P5obcMW3vIrZ8)
bot_user_id = "user_P5obcMW3vIrZ8"
company_id = "biz_Vwsite2gfnFBU2"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pfile_bot = os.path.join(base_dir, "profiles", "bots", bot_user_id, "profile.json")
if not os.path.exists(pfile_bot):
    print(f"Profile file not found for bot {bot_user_id}")
    exit()

with open(pfile_bot, "r", encoding="utf-8") as f:
    bot_data = json.load(f)

os.environ["BOT_USER_ID"] = bot_user_id
os.environ["WHOP_COMPANY_ID"] = company_id
os.environ["WHOP_EXPERIENCE_ID"] = action.get("experience_id") or ""
os.environ["WHOP_OAUTH_TOKEN"] = bot_data.get("oauth_token", "")
os.environ["WHOP_REFRESH_TOKEN"] = bot_data.get("refresh_token", "")

print(f"Attempting to post as bot user {bot_user_id}...")
try:
    post_data = post_to_forum(
        experience_id=action.get("experience_id"),
        content=action.get("content", ""),
        title=action.get("title", ""),
        pinned=False,
        is_mention=False,
        visibility="members_only",
        company_id=company_id,
        bot_user_id=bot_user_id
    )
    print("\nResult of post_to_forum:", post_data)
    
    # Try importing post_to_forum LAST_ERROR
    import post_to_forum as ptf_mod
    print("LAST_ERROR:", getattr(ptf_mod, "LAST_ERROR", None))
except Exception as e:
    print("Exception occurred:", e)
