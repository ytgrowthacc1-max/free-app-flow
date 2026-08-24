import sys
import os
sys.path.insert(0, r"c:\Python\WHOP AUTOMATION AGENTIC\execution")
import json
import requests
from whop_auth import get_fresh_token

bot_user_id = os.getenv("BOT_USER_ID", "user_gAkQk98I3AyP4")
token = get_fresh_token(bot_user_id)

print(f"Bot User ID: {bot_user_id}")
print(f"Token present: {bool(token)}")
if token:
    print(f"Token snippet: {token[:25]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bot_dir = os.path.join(base_dir, "profiles", "bots", bot_user_id)

comp_list = []
if os.path.exists(bot_dir):
    for item in os.listdir(bot_dir):
        item_path = os.path.join(bot_dir, item)
        if os.path.isdir(item_path):
            cfile = os.path.join(item_path, "company.json")
            if os.path.exists(cfile):
                try:
                    with open(cfile, "r", encoding="utf-8") as f:
                        cinfo = json.load(f)
                    if not cinfo.get("hidden", False):
                        comp_list.append(cinfo)
                except Exception as e:
                    pass

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

t0 = time.time()
print(f"Total non-hidden companies in bot dir: {len(comp_list)}")

all_forums = []
seen_ids = set()

def _fetch_company_exps(cinfo):
    cid = cinfo.get("company_id")
    cname = cinfo.get("company_name", "Community")
    if not cid:
        return []
    found = []
    url = f"https://api.whop.com/api/v1/experiences?company_id={cid}"
    try:
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            exps = r.json().get("data", [])
            for exp in exps:
                app_info = exp.get("app", {})
                if app_info.get("id") == "app_dYfm2IdXhDMquv" or app_info.get("name") == "Forums":
                    eid = exp.get("id")
                    ename = exp.get("name") or "Forum"
                    found.append({
                        "id": eid,
                        "name": f"{cname} - {ename}",
                        "company_name": cname,
                        "company_id": cid,
                        "is_public": exp.get("is_public", False)
                    })
    except Exception as ce:
        pass
    
    local_exp = cinfo.get("experience_id")
    if local_exp and not any(f["id"] == local_exp for f in found):
        found.append({
            "id": local_exp,
            "name": f"{cname} - Public Forum",
            "company_name": cname,
            "company_id": cid,
            "is_public": True
        })
    return found

with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_cinfo = {executor.submit(_fetch_company_exps, cinfo): cinfo for cinfo in comp_list}
    for future in as_completed(future_to_cinfo):
        try:
            res_items = future.result()
            for item in res_items:
                eid = item.get("id")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    all_forums.append(item)
        except Exception:
            pass

for cinfo in comp_list:
    cid = cinfo.get("company_id")
    cname = cinfo.get("company_name", "Community")
    local_exp = cinfo.get("experience_id")
    if local_exp and local_exp not in seen_ids:
        seen_ids.add(local_exp)
        all_forums.append({
            "id": local_exp,
            "name": f"{cname} - Public Forum",
            "company_name": cname,
            "company_id": cid,
            "is_public": True
        })

t1 = time.time()
print(f"\nCompleted in {t1 - t0:.2f} seconds!")
print(f"Final all_forums count: {len(all_forums)}")
for f in all_forums[:10]:
    print(f)
