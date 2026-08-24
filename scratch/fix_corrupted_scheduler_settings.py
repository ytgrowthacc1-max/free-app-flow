import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")
fixed_count = 0

default_secondary_sjson = {
    "master_switch_enabled": False,
    "chatbot_enabled": False,
    "followups_enabled": False,
    "scheduler_enabled": False,
    "autopilot_enabled": False,
    "reshare_enabled": False,
    "frequency_minutes": 60,
    "random_delay_max_minutes": 15,
    "min_posts_per_day": 12,
    "max_posts_per_day": 24,
    "allowed_post_types": ["poll"]
}

for bot_id in os.listdir(bots_dir):
    bpath = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bpath):
        continue
    
    for item in os.listdir(bpath):
        ipath = os.path.join(bpath, item)
        if os.path.isdir(ipath):
            sfile = os.path.join(ipath, "scheduler_settings.json")
            cfile = os.path.join(ipath, "company.json")
            
            is_corrupted = False
            if os.path.exists(sfile):
                try:
                    if os.path.getsize(sfile) == 0:
                        is_corrupted = True
                    else:
                        with open(sfile, "r", encoding="utf-8") as sf:
                            json.load(sf)
                except Exception:
                    is_corrupted = True
            
            if is_corrupted:
                # Read experience_id from company.json if available
                exp_id = ""
                if os.path.exists(cfile):
                    try:
                        with open(cfile, "r", encoding="utf-8") as cf:
                            exp_id = json.load(cf).get("experience_id", "")
                    except Exception:
                        pass
                
                sdata = dict(default_secondary_sjson)
                if exp_id:
                    sdata["experience_id"] = exp_id
                    sdata["experience_ids"] = [exp_id]
                
                with open(sfile, "w", encoding="utf-8") as sf:
                    json.dump(sdata, sf, indent=2)
                
                fixed_count += 1
                print(f"[REPAIRED] Corrupted scheduler_settings.json for bot {bot_id} | CID: {item}")

print(f"\nRepaired {fixed_count} corrupted scheduler_settings.json files.")
