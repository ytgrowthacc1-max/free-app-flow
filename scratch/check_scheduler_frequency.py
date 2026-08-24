import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

if not os.path.exists(bots_dir):
    print("No profiles/bots directory.")
    exit()

master_configs = []

for bot_id in os.listdir(bots_dir):
    bpath = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bpath):
        continue
    
    pfile = os.path.join(bpath, "profile.json")
    uname = bot_id
    if os.path.exists(pfile):
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                uname = json.load(f).get("bot_username", bot_id)
        except Exception:
            pass
            
    for item in os.listdir(bpath):
        ipath = os.path.join(bpath, item)
        if os.path.isdir(ipath):
            sfile = os.path.join(ipath, "scheduler_settings.json")
            cfile = os.path.join(ipath, "company.json")
            if os.path.exists(sfile) and os.path.exists(cfile):
                try:
                    with open(sfile, "r", encoding="utf-8") as sf:
                        sdata = json.load(sf)
                    with open(cfile, "r", encoding="utf-8") as cf:
                        cdata = json.load(cf)
                        
                    if sdata.get("master_switch_enabled", False) and (sdata.get("scheduler_enabled", False) or sdata.get("autopilot_enabled", False)):
                        master_configs.append({
                            "bot": uname,
                            "community": cdata.get("company_name"),
                            "freq_min": sdata.get("frequency_minutes"),
                            "rand_delay": sdata.get("random_delay_max_minutes"),
                            "min_posts": sdata.get("min_posts_per_day"),
                            "max_posts": sdata.get("max_posts_per_day"),
                            "posts_today": sdata.get("posts_published_today", 0),
                            "last_run": sdata.get("last_run_time", 0.0)
                        })
                except Exception:
                    pass

print(f"Total Active Master Schedulers: {len(master_configs)}\n")
for idx, mc in enumerate(master_configs, 1):
    print(f"{idx}. @{mc['bot']} | Community: '{mc['community']}'")
    print(f"   Frequency: Every {mc['freq_min']} mins (delay max +/- {mc['rand_delay']}m)")
    print(f"   Daily Range: {mc['min_posts']} to {mc['max_posts']} posts/day | Published Today: {mc['posts_today']}")
    print(f"   Last Run Timestamp: {mc['last_run']}\n")
