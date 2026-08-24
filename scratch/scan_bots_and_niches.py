import os
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

existing_bots = []
fresh_bots = []
niches = {}

for b in sorted(os.listdir(bots_dir)):
    bpath = os.path.join(bots_dir, b)
    if not os.path.isdir(bpath):
        continue
    
    subdirs = [d for d in os.listdir(bpath) if os.path.isdir(os.path.join(bpath, d))]
    comp_dirs = [d for d in subdirs if d.startswith("biz_") or d.startswith("comp_")]
    files = [f for f in os.listdir(bpath) if os.path.isfile(os.path.join(bpath, f))]
    
    username = None
    uinfo_path = os.path.join(bpath, "user_info.json")
    if os.path.exists(uinfo_path):
        try:
            with open(uinfo_path, "r", encoding="utf-8") as f:
                udata = json.load(f)
                username = udata.get("username") or udata.get("name")
        except Exception:
            pass
            
    if not username:
        tpath = os.path.join(bpath, "oauth_tokens.json")
        if os.path.exists(tpath):
            try:
                with open(tpath, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    username = tdata.get("username")
            except Exception:
                pass

    has_token = "oauth_tokens.json" in files or "token.json" in files

    # Scan existing niches
    for cd in comp_dirs:
        cdpath = os.path.join(bpath, cd)
        fsettings = os.path.join(cdpath, "forum_settings.json")
        cjson = os.path.join(cdpath, "company.json")
        ssettings = os.path.join(cdpath, "scheduler_settings.json")
        cname = None
        is_master = False
        if os.path.exists(cjson):
            try:
                with open(cjson, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    cname = cdata.get("company_name")
                    is_master = cdata.get("pinned", False) or cdata.get("starred", False)
            except Exception:
                pass
        if os.path.exists(ssettings):
            try:
                with open(ssettings, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                    if sdata.get("master_switch_enabled") and sdata.get("autopilot_enabled"):
                        is_master = True
            except Exception:
                pass

        if os.path.exists(fsettings):
            try:
                with open(fsettings, "r", encoding="utf-8") as f:
                    fdata = json.load(f)
                    bname = fdata.get("business_name")
                    if bname and (is_master or bname not in niches):
                        niches[bname] = {
                            "bot_id": b,
                            "username": username,
                            "comp_id": cd,
                            "title": cname,
                            "is_master": is_master,
                            "pain_points": len(fdata.get("pain_points", [])),
                            "custom_prompts": len(fdata.get("custom_prompts", [])),
                            "comment_links": len(fdata.get("comment_links", []))
                        }
            except Exception:
                pass

    if len(comp_dirs) == 0:
        fresh_bots.append({
            "bot_id": b,
            "username": username,
            "has_token": has_token,
            "files": files
        })
    else:
        existing_bots.append({
            "bot_id": b,
            "username": username,
            "comp_count": len(comp_dirs)
        })

print(f"Total bot profiles: {len(os.listdir(bots_dir))}")
print(f"Bots with existing communities: {len(existing_bots)}")
print(f"Fresh bots (0 communities): {len(fresh_bots)}")

print("\n--- FRESH BOT PROFILES (0 Communities) ---")
for fb in fresh_bots:
    print(f"  {fb['bot_id']} (@{fb['username']}) - token: {fb['has_token']} - files: {fb['files']}")

print("\n--- DISCOVERED BUSINESSES / NICHES ---")
for k, v in niches.items():
    print(f"  Business: '{k}' | Master: {v['is_master']} | Bot: @{v['username']} ({v['bot_id']}/{v['comp_id']}) | Title: {v['title']} | Prompts: {v['custom_prompts']}, PPs: {v['pain_points']}, Links: {v['comment_links']}")
