import os
import glob
import json
import sys

sys.path.insert(0, "execution")
from whop_auth import get_fresh_token

bot_dirs = glob.glob("profiles/bots/*")
print(f"Checking {len(bot_dirs)} bot profiles for refresh...\n")

refreshed_success = 0
failed_count = 0

for bdir in bot_dirs:
    if not os.path.isdir(bdir):
        continue
    bot_id = os.path.basename(bdir)
    pfile = os.path.join(bdir, "profile.json")
    if not os.path.exists(pfile):
        continue
    
    with open(pfile, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    bot_name = data.get("bot_username", bot_id)
    # Clear flag temporarily to attempt refresh
    if data.get("refresh_token_invalid"):
        data["refresh_token_invalid"] = False
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    try:
        token = get_fresh_token(bot_id)
        if token:
            print(f"[OK] Bot @{bot_name} ({bot_id}): Valid token active.")
            refreshed_success += 1
        else:
            print(f"[FAIL] Bot @{bot_name} ({bot_id}): Refresh failed or requires re-auth.")
            failed_count += 1
    except Exception as e:
        print(f"[FAIL] Bot @{bot_name} ({bot_id}): Refresh failed ({e}). Setting refresh_token_invalid=True.")
        with open(pfile, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["refresh_token_invalid"] = True
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        failed_count += 1

print(f"\nSummary: {refreshed_success} active/refreshed, {failed_count} expired.")
