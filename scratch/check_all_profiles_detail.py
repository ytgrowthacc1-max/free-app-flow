import os
import glob
import json

profiles_dir = "profiles"
for root, dirs, files in os.walk(profiles_dir):
    if "profile.json" in files:
        pfile = os.path.join(root, "profile.json")
        sfile = os.path.join(root, "scheduler_settings.json")
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                pdata = json.load(f)
            sdata = {}
            if os.path.exists(sfile):
                with open(sfile, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
            
            pname = pdata.get("name") or pdata.get("username")
            valid = pdata.get("valid", True)
            print(f"\nPath: {root}")
            print(f"  Name: {pname} | User ID: {pdata.get('user_id')} | Company ID: {pdata.get('company_id')}")
            print(f"  Valid: {valid} | Expired Msg: {pdata.get('error_message')}")
            print(f"  Scheduler Active: {sdata.get('active')} | Autopilot: {sdata.get('autopilot_active')} | Time Window: {sdata.get('start_time')}-{sdata.get('end_time')}")
        except Exception as e:
            print(f"Error reading {pfile}: {e}")
