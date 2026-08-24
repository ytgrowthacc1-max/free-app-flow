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

print(f"Ensuring Forum experiences for ALL communities of bot {bot_user_id}...")

created_count = 0
existing_count = 0

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

    # 1. Fetch experiences from Whop API
    url = f"https://api.whop.com/api/v1/experiences?company_id={cid}"
    res = requests.get(url, headers=headers, timeout=10)

    forum_exp_id = None
    if res.status_code == 200:
        data = res.json().get("data", [])
        for exp in data:
            app_info = exp.get("app", {})
            if app_info.get("id") == "app_dYfm2IdXhDMquv" or app_info.get("name") == "Forums":
                forum_exp_id = exp.get("id")
                break

    # 2. If no forum app experience exists, create one via POST /experiences
    if not forum_exp_id:
        create_url = "https://api.whop.com/api/v1/experiences"
        payload = {
            "app_id": "app_dYfm2IdXhDMquv",
            "company_id": cid,
            "name": "Public Forum",
            "is_public": True
        }
        cres = requests.post(create_url, headers=headers, json=payload, timeout=10)
        if cres.status_code in [200, 201]:
            exp_data = cres.json()
            forum_exp_id = exp_data.get("id")
            created_count += 1
            print(f"[CREATED FORUM] {cname} ({cid}) -> {forum_exp_id}")
        else:
            print(f"[ERROR CREATING] {cname} ({cid}): {cres.status_code} - {cres.text}")
    else:
        existing_count += 1
        print(f"[EXISTING FORUM] {cname} ({cid}) -> {forum_exp_id}")

    # 3. Update company.json if experience_id changed or was missing
    if forum_exp_id and cinfo.get("experience_id") != forum_exp_id:
        cinfo["experience_id"] = forum_exp_id
        with open(cfile, "w", encoding="utf-8") as f:
            json.dump(cinfo, f, indent=2)

print(f"\nCompleted!")
print(f"Existing forums: {existing_count}")
print(f"Newly created forums: {created_count}")
print(f"Total processed: {existing_count + created_count}")
