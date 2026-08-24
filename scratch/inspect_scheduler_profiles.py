import os
import json

base_dir = r"C:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

if not os.path.exists(bots_dir):
    print("No bots directory found.")
    exit()

for bot_id in os.listdir(bots_dir):
    bot_path = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bot_path):
        continue
    
    pfile = os.path.join(bot_path, "profile.json")
    bot_username = "Unknown"
    if os.path.exists(pfile):
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                pdata = json.load(f)
                bot_username = pdata.get("bot_username", "Unknown")
        except Exception as e:
            bot_username = f"Error: {e}"
            
    print(f"\nBot ID: {bot_id} (@{bot_username})")
    
    for sub in os.listdir(bot_path):
        sub_path = os.path.join(bot_path, sub)
        if not os.path.isdir(sub_path):
            continue
        
        comp_file = os.path.join(sub_path, "company.json")
        comp_name = sub
        hidden = False
        if os.path.exists(comp_file):
            try:
                with open(comp_file, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    comp_name = cdata.get("company_name", sub)
                    hidden = cdata.get("hidden", False)
            except Exception:
                pass
        
        sched_file = os.path.join(sub_path, "scheduler_settings.json")
        has_sched = os.path.exists(sched_file)
        sched_summary = "None"
        if has_sched:
            try:
                with open(sched_file, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                    sched_summary = f"Enabled: {sdata.get('autopilot_enabled')}, Time window: {sdata.get('time_window_start')}-{sdata.get('time_window_end')}, Max posts: {sdata.get('max_posts_per_day')}"
            except Exception as e:
                sched_summary = f"Error reading: {e}"
                
        print(f"  - Company: {comp_name} ({sub}) | Hidden: {hidden} | Scheduler: {sched_summary}")
