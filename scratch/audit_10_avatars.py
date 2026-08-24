import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from whop_auth import get_fresh_token
from provision_10_fresh_networks import FLEET_SPECIFICATIONS

print(f"{'#':<3} {'Username':<20} {'Bot ID':<22} {'Niche':<20} {'Avatar Status'}")
print("-" * 80)

for idx, spec in enumerate(FLEET_SPECIFICATIONS, 1):
    bot_id = spec["bot_id"]
    username = spec["username"]
    niche = spec["niche"]
    
    token = get_fresh_token(bot_id)
    if not token:
        print(f"{idx:<3} @{username:<19} {bot_id:<22} {niche:<20} NO TOKEN")
        continue
        
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get("https://api.whop.com/v1/users/me", headers=headers, timeout=10)
        if resp.status_code == 200:
            user = resp.json()
            pic = user.get("profile_picture")
            url = pic.get("url") if pic else None
            is_custom = bool(url and "default" not in url.lower() and "assets-2-prod.whop.com" in url.lower())
            status = "CUSTOM HUMAN" if is_custom else ("DEFAULT / NONE" if not url else f"OTHER ({url[:30]}...)")
            print(f"{idx:<3} @{username:<19} {bot_id:<22} {niche:<20} {status}")
        else:
            print(f"{idx:<3} @{username:<19} {bot_id:<22} {niche:<20} HTTP {resp.status_code}")
    except Exception as e:
        print(f"{idx:<3} @{username:<19} {bot_id:<22} {niche:<20} ERROR: {e}")
