import os, json

base_dir = r"profiles"
bots_dir = os.path.join(base_dir, "bots")

print("--- Searching in profiles/ ---")
if os.path.exists(base_dir):
    for item in os.listdir(base_dir):
        if item == "bots": continue
        p = os.path.join(base_dir, item)
        if os.path.isdir(p):
            pfile = os.path.join(p, "profile.json")
            if os.path.exists(pfile):
                with open(pfile, "r", encoding="utf-8") as f:
                    d = json.load(f)
                print(f"Legacy profile: {item} -> company_id={d.get('company_id')}, bot={d.get('bot_username')}")

print("\n--- Searching in profiles/bots/ ---")
if os.path.exists(bots_dir):
    for bot in os.listdir(bots_dir):
        bpath = os.path.join(bots_dir, bot)
        if os.path.isdir(bpath):
            pfile = os.path.join(bpath, "profile.json")
            bot_name = bot
            if os.path.exists(pfile):
                with open(pfile, "r", encoding="utf-8") as f:
                    bot_name = json.load(f).get("bot_username", bot)
            for citem in os.listdir(bpath):
                cpath = os.path.join(bpath, citem)
                if os.path.isdir(cpath) and citem.startswith("biz_"):
                    cfile = os.path.join(cpath, "company.json")
                    cname = citem
                    if os.path.exists(cfile):
                        with open(cfile, "r", encoding="utf-8") as f:
                            cd = json.load(f)
                        cname = cd.get("title", cd.get("company_name", citem))
                        exp_id = cd.get("experience_id")
                        print(f"Bot @{bot_name} ({bot}) -> Company: {cname} ({citem}), exp_id={exp_id}")
