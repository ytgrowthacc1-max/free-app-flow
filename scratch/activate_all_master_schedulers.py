import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from provision_10_fresh_networks import FLEET_SPECIFICATIONS
from provision_batch2_networks import BATCH2_SPECIFICATIONS

ALL_SPECS = FLEET_SPECIFICATIONS + BATCH2_SPECIFICATIONS

active_slots_24_7 = {
    "mon": {"enabled": True, "start": "00:00", "end": "23:59"},
    "tue": {"enabled": True, "start": "00:00", "end": "23:59"},
    "wed": {"enabled": True, "start": "00:00", "end": "23:59"},
    "thu": {"enabled": True, "start": "00:00", "end": "23:59"},
    "fri": {"enabled": True, "start": "00:00", "end": "23:59"},
    "sat": {"enabled": True, "start": "00:00", "end": "23:59"},
    "sun": {"enabled": True, "start": "00:00", "end": "23:59"}
}

updated_count = 0

for spec in ALL_SPECS:
    bot_id = spec["bot_id"]
    user = spec["username"]
    master_title = spec.get("master_title") or spec.get("niche")
    
    bot_dir = os.path.join(BASE_DIR, "profiles", "bots", bot_id)
    if not os.path.exists(bot_dir):
        continue
        
    for d in os.listdir(bot_dir):
        cdir = os.path.join(bot_dir, d)
        if not os.path.isdir(cdir): continue
        cjson = os.path.join(cdir, "company.json")
        sjson = os.path.join(cdir, "scheduler_settings.json")
        if not os.path.exists(cjson) or not os.path.exists(sjson):
            continue
            
        cdata = json.load(open(cjson, encoding="utf-8"))
        if cdata.get("pinned") or cdata.get("starred") or cdata.get("is_master"):
            sdata = json.load(open(sjson, encoding="utf-8"))
            sdata["master_switch_enabled"] = True
            sdata["scheduler_enabled"] = True
            sdata["autopilot_enabled"] = True
            sdata["reshare_enabled"] = True
            sdata["reshare_auto_interact"] = True
            sdata["frequency_minutes"] = 3
            sdata["random_delay_max_minutes"] = 3
            sdata["min_posts_per_day"] = 200
            sdata["max_posts_per_day"] = 300
            sdata["active_slots"] = active_slots_24_7
            sdata["last_run_time"] = 0.0 # Trigger immediate post on next tick!
            
            exp_id = cdata.get("experience_id", "")
            if exp_id:
                sdata["experience_id"] = exp_id
                sdata["experience_ids"] = [exp_id]
                
            with open(sjson, "w", encoding="utf-8") as sf:
                json.dump(sdata, sf, indent=2)
            updated_count += 1
            print(f"[ACTIVE] Configured Master Scheduler for @{user} ({cdata.get('company_name')}) -> 24/7 Autopilot ON, Frequency: 3m")

print(f"\n[SUCCESS] Activated 24/7 Autopilot on {updated_count}/20 Master Hubs!")
