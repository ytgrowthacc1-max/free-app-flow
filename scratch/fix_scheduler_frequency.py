import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")
updated_count = 0

for bot_id in os.listdir(bots_dir):
    bpath = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bpath):
        continue
    
    for item in os.listdir(bpath):
        ipath = os.path.join(bpath, item)
        if os.path.isdir(ipath):
            sfile = os.path.join(ipath, "scheduler_settings.json")
            cfile = os.path.join(ipath, "company.json")
            if os.path.exists(sfile) and os.path.exists(cfile):
                try:
                    with open(sfile, "r", encoding="utf-8") as sf:
                        sdata = json.load(sf)
                except Exception as e:
                    print(f"Skipping corrupted JSON: {sfile} ({e})")
                    continue
                
                # Check if this is an active master scheduler
                if sdata.get("master_switch_enabled", False) and (sdata.get("scheduler_enabled", False) or sdata.get("autopilot_enabled", False)):
                    changed = False
                    if sdata.get("frequency_minutes") != 3:
                        sdata["frequency_minutes"] = 3
                        changed = True
                    if sdata.get("random_delay_max_minutes") != 3:
                        sdata["random_delay_max_minutes"] = 3
                        changed = True
                    if sdata.get("min_posts_per_day") != 200:
                        sdata["min_posts_per_day"] = 200
                        changed = True
                    if sdata.get("max_posts_per_day") != 300:
                        sdata["max_posts_per_day"] = 300
                        changed = True
                        
                    if changed:
                        try:
                            with open(sfile, "w", encoding="utf-8") as sf:
                                json.dump(sdata, sf, indent=2)
                            updated_count += 1
                            cname = "Unknown"
                            with open(cfile, "r", encoding="utf-8") as cf:
                                cname = json.load(cf).get("company_name", "Unknown")
                            print(f"[UPDATED] Bot {bot_id} | Master: '{cname}' -> Freq=3m, Max=300 posts/day")
                        except Exception as write_err:
                            print(f"Write error for {sfile}: {write_err}")

print(f"\nDone. Updated {updated_count} master schedulers.")
