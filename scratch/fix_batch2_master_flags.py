import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from provision_batch2_networks import BATCH2_SPECIFICATIONS, configure_master_scheduler, disable_secondary_scheduler

for spec in BATCH2_SPECIFICATIONS:
    idx = spec["index"]
    bot_id = spec["bot_id"]
    user = spec["username"]
    master_title = spec["master_title"]
    
    bot_dir = os.path.join(BASE_DIR, "profiles", "bots", bot_id)
    if not os.path.exists(bot_dir):
        continue
        
    master_cid = None
    master_exp = None
    secondary_exps = []
    
    # 1. Identify Master vs Secondaries
    for d in os.listdir(bot_dir):
        cdir = os.path.join(bot_dir, d)
        if not os.path.isdir(cdir):
            continue
        cjson_path = os.path.join(cdir, "company.json")
        if not os.path.exists(cjson_path):
            continue
            
        cdata = json.load(open(cjson_path, encoding="utf-8"))
        cname = cdata.get("company_name", "")
        exp_id = cdata.get("experience_id", "")
        
        if cname.lower() == master_title.lower() or cdata.get("is_master") or cdata.get("pinned"):
            master_cid = d
            master_exp = exp_id
            cdata["pinned"] = True
            cdata["starred"] = True
            cdata["is_master"] = True
            with open(cjson_path, "w", encoding="utf-8") as cf:
                json.dump(cdata, cf, indent=2)
        else:
            cdata["pinned"] = False
            cdata["starred"] = False
            cdata["is_master"] = False
            with open(cjson_path, "w", encoding="utf-8") as cf:
                json.dump(cdata, cf, indent=2)
            disable_secondary_scheduler(cdir)
            if exp_id:
                secondary_exps.append(exp_id)
                
    if master_cid and master_exp:
        master_dir = os.path.join(bot_dir, master_cid)
        configure_master_scheduler(master_dir, master_exp, secondary_exps)
        print(f"[FIXED] Bot #{idx:02d}: @{user:<20} Master: {master_cid} (Exp: {master_exp}) | Linked {len(secondary_exps)} secondaries")
    else:
        print(f"[ERROR] Bot #{idx:02d}: @{user:<20} Master not found for title '{master_title}'")

print("\nRunning Full 20-Bot Fleet Audit...")
from provision_batch2_networks import audit_fleet
audit_fleet()
