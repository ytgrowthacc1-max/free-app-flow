import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

print("Checking profiles in:", bots_dir)
if os.path.exists(bots_dir):
    for bot_id in os.listdir(bots_dir):
        bot_path = os.path.join(bots_dir, bot_id)
        if not os.path.isdir(bot_path):
            continue
        pfile = os.path.join(bot_path, "profile.json")
        if not os.path.exists(pfile):
            print(f"[MISSING PROFILE.JSON] {bot_id}")
            continue
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                pdata = json.load(f)
            # check companies
            companies = []
            for item in os.listdir(bot_path):
                ipath = os.path.join(bot_path, item)
                if os.path.isdir(ipath):
                    cfile = os.path.join(ipath, "company.json")
                    if os.path.exists(cfile):
                        with open(cfile, "r", encoding="utf-8") as cf:
                            cdata = json.load(cf)
                        companies.append(cdata.get("company_name", item))
            print(f"[OK] {pdata.get('bot_username')} ({bot_id}) -> {len(companies)} communities ({', '.join(companies)})")
        except Exception as e:
            print(f"[ERROR JSON] {bot_id}: {e}")
