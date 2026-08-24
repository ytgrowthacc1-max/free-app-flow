import os
import sys
import json
import requests

sys.path.insert(0, r"c:\Python\WHOP AUTOMATION AGENTIC\execution")
from whop_auth import get_fresh_token

bot_user_id = os.getenv("BOT_USER_ID", "user_gAkQk98I3AyP4")
token = get_fresh_token(bot_user_id)
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bot_dir = os.path.join(base_dir, "profiles", "bots", bot_user_id)

print(f"Checking 41 companies for bot {bot_user_id}...")

no_forum_found = []
updated_count = 0
already_had_count = 0

for item in sorted(os.listdir(bot_dir)):
    item_path = os.path.join(bot_dir, item)
    if not os.path.isdir(item_path):
        continue
    cfile = os.path.join(item_path, "company.json")
    if not os.path.exists(cfile):
        continue

    with open(cfile, "r", encoding="utf-8") as f:
        cinfo = json.load(f)

    cid = cinfo.get("company_id")
    cname = cinfo.get("company_name", item)
    current_exp = cinfo.get("experience_id")

    url = f"https://api.whop.com/api/v1/experiences?company_id={cid}"
    res = requests.get(url, headers=headers, timeout=10)

    forum_exp = None
    all_exps = []
    if res.status_code == 200:
        data = res.json().get("data", [])
        all_exps = data
        for exp in data:
            app_info = exp.get("app", {})
            if app_info.get("id") == "app_dYfm2IdXhDMquv" or app_info.get("name") == "Forums":
                forum_exp = exp
                break

    if forum_exp:
        eid = forum_exp.get("id")
        if current_exp != eid:
            cinfo["experience_id"] = eid
            with open(cfile, "w", encoding="utf-8") as f:
                json.dump(cinfo, f, indent=2)
            print(f"[UPDATED] {cname} ({cid}): set experience_id -> {eid}")
            updated_count += 1
        else:
            already_had_count += 1
    else:
        print(f"[NO FORUM FOUND] {cname} ({cid}) - total exps on Whop: {len(all_exps)}")
        for e in all_exps:
            print(f"   Exp: {e.get('name')} | App: {e.get('app', {}).get('name')} ({e.get('app', {}).get('id')})")
        no_forum_found.append((cid, cname, cfile, all_exps))

print(f"\nSummary:")
print(f"Already had matching forum: {already_had_count}")
print(f"Updated with found forum: {updated_count}")
print(f"No forum app found on Whop: {len(no_forum_found)}")
