import os
import sys
import json
import glob

sys.path.append('execution')

print("--- Inspecting Profiles & Pending Queue ---")

profiles_dir = "profiles"
if os.path.exists(profiles_dir):
    for pdir in glob.glob(os.path.join(profiles_dir, "*")):
        if os.path.isdir(pdir):
            pname = os.path.basename(pdir)
            prof_file = os.path.join(pdir, "profile.json")
            sched_file = os.path.join(pdir, "scheduler_settings.json")
            
            pdata = {}
            sdata = {}
            if os.path.exists(prof_file):
                with open(prof_file, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
            if os.path.exists(sched_file):
                with open(sched_file, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                    
            print(f"\nProfile: {pname} ({pdata.get('name', 'N/A')})")
            print(f"  Company ID: {pdata.get('company_id')}")
            print(f"  Scheduler Active: {sdata.get('active', False)}")
            print(f"  Frequency: {sdata.get('frequency_mins')} mins")
            print(f"  Last Run: {sdata.get('last_run')}")
            print(f"  Posts Today: {sdata.get('posts_today')}")
            
print("\n--- Inspecting Pending Queue Database / JSON ---")

try:
    import pending_db
    pending = pending_db.get_pending_posts()
    print(f"Total Pending Posts in DB: {len(pending)}")
    for item in pending:
        print(f"  ID: {item.get('id')} | Profile: {item.get('profile_id')} | Title: {item.get('title')[:30]} | Status: {item.get('status')}")
except Exception as e:
    print(f"Error inspecting pending_db: {e}")

tmp_files = glob.glob(".tmp/*")
print(f"\nFiles in .tmp/: {tmp_files}")
