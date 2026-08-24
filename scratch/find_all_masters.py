import os
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

master_communities = []

for b in sorted(os.listdir(bots_dir)):
    bpath = os.path.join(bots_dir, b)
    if not os.path.isdir(bpath): continue
    
    pdata = {}
    pfile = os.path.join(bpath, "profile.json")
    if os.path.exists(pfile):
        try: pdata = json.load(open(pfile, encoding="utf-8"))
        except: pass
    username = pdata.get("bot_username", b)

    for d in os.listdir(bpath):
        cdir = os.path.join(bpath, d)
        if not os.path.isdir(cdir) or not (d.startswith("biz_") or d.startswith("comp_")):
            continue
        
        cjson = os.path.join(cdir, "company.json")
        sjson = os.path.join(cdir, "scheduler_settings.json")
        fjson = os.path.join(cdir, "forum_settings.json")
        ijson = os.path.join(cdir, "chatbot_instructions.md")

        cdata = {}
        sdata = {}
        fdata = {}
        has_instr = os.path.exists(ijson)

        if os.path.exists(cjson):
            try: cdata = json.load(open(cjson, encoding="utf-8"))
            except: pass
        if os.path.exists(sjson):
            try: sdata = json.load(open(sjson, encoding="utf-8"))
            except: pass
        if os.path.exists(fjson):
            try: fdata = json.load(open(fjson, encoding="utf-8"))
            except: pass

        is_master = (
            cdata.get("pinned") or 
            cdata.get("starred") or 
            (sdata.get("master_switch_enabled") and sdata.get("autopilot_enabled") and len(sdata.get("reshare_experience_ids", [])) > 0)
        )

        if is_master:
            master_communities.append({
                "bot_id": b,
                "username": username,
                "comp_id": d,
                "company_name": cdata.get("company_name"),
                "business_name": fdata.get("business_name"),
                "business_description": fdata.get("business_description"),
                "reshare_count": len(sdata.get("reshare_experience_ids", [])),
                "frequency_minutes": sdata.get("frequency_minutes"),
                "pain_points": len(fdata.get("pain_points", [])),
                "custom_prompts": len(fdata.get("custom_prompts", [])),
                "comment_links": len(fdata.get("comment_links", [])),
                "has_chatbot_instructions": has_instr,
                "allowed_post_types": sdata.get("allowed_post_types") or fdata.get("allowed_post_types")
            })

print(f"Total Master Communities Found: {len(master_communities)}")
for idx, m in enumerate(master_communities, 1):
    print(f"\n[{idx}] {m['company_name']} ({m['business_name']})")
    print(f"    Bot: @{m['username']} ({m['bot_id']}) | Comp: {m['comp_id']}")
    print(f"    Reshares: {m['reshare_count']} | Frequency: {m['frequency_minutes']}m | Post Types: {m['allowed_post_types']}")
    print(f"    Prompts: {m['custom_prompts']} | PPs: {m['pain_points']} | Links: {m['comment_links']} | Instr: {m['has_chatbot_instructions']}")
