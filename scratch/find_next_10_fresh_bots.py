import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from whop_auth import get_fresh_token

bots_dir = os.path.join(BASE_DIR, "profiles", "bots")
candidates = []

for bot_id in sorted(os.listdir(bots_dir)):
    bdir = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bdir):
        continue
        
    pjson_path = os.path.join(bdir, "profile.json")
    if not os.path.exists(pjson_path):
        continue
        
    pdata = json.load(open(pjson_path, encoding="utf-8"))
    if pdata.get("suspended"):
        continue
        
    # Count existing communities
    subdirs = [d for d in os.listdir(bdir) if os.path.isdir(os.path.join(bdir, d)) and (d.startswith("biz_") or d.startswith("comp_"))]
    if len(subdirs) > 0:
        continue # Not a fresh bot
        
    username = pdata.get("bot_username") or pdata.get("username") or bot_id
    token = get_fresh_token(bot_id)
    if not token:
        continue
        
    # Verify token scope with Whop API
    try:
        h = {"Authorization": f"Bearer {token}"}
        r = requests.get("https://api.whop.com/v1/users/me", headers=h, timeout=8)
        if r.status_code == 200:
            candidates.append({
                "bot_id": bot_id,
                "username": username,
                "email": pdata.get("email", "")
            })
    except Exception:
        pass

print(f"Found {len(candidates)} completely fresh valid bots with 0 communities:")
for idx, c in enumerate(candidates[:15], 1):
    print(f"{idx:02d}. @{c['username']} ({c['bot_id']}) - {c['email']}")
