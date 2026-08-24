import os
import sys
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

# The 10 Target Niches we want to rotate across the 10 fresh accounts:
# 1. Revenue Apps (e.g. user_eSN5Z4XrLT0ZQ / biz_VHlv37S71ESE1G)
# 2. XP Arena (e.g. user_lO14mFc5tBKN3 / biz_pV1MfpPbaGydou)
# 3. The Tools Pack (e.g. user_UCUWNo0s132ET / biz_c9ai0lCMJoCw9e)
# 4. Flip Empire (e.g. user_puyTsi9E4vLkP / biz_LK1qoXTov4CsLA)
# 5. Cash City Picks (e.g. user_HVCjzjUye5q5I / biz_IR9QwwEFeC199z)
# 6. Deal Gains (e.g. user_PUpL8cbyE1Zf2 / biz_62x0KF1HwUkUd2)
# 7. Deal Soldier (e.g. user_mnR4EbynVY8UA / biz_Epy3Gq1LkscDbI)
# 8. Poke Alerts (e.g. user_VXlrbVwms4laY / biz_3wuSbLPNZb4mU7)
# 9. Crystal Academy Hub (e.g. user_lMrwnvtkSSp6w / biz_wIrZm2C9eZmsFB)
# 10. Official Picks VIP (e.g. user_pdd7UFzVXqlg4 / biz_06H1NGZWgkCioO)

BENCHMARKS = [
    {"niche": "Revenue Apps", "master_title": "Revenue Apps VIP", "src_bot": "user_eSN5Z4XrLT0ZQ", "src_comp": "biz_VHlv37S71ESE1G"},
    {"niche": "XP Arena", "master_title": "XP Arena VIP", "src_bot": "user_lO14mFc5tBKN3", "src_comp": "biz_pV1MfpPbaGydou"},
    {"niche": "The Tools Pack", "master_title": "The Tools Pack VIP", "src_bot": "user_UCUWNo0s132ET", "src_comp": "biz_c9ai0lCMJoCw9e"},
    {"niche": "Flip Empire", "master_title": "Flip Empire VIP", "src_bot": "user_puyTsi9E4vLkP", "src_comp": "biz_LK1qoXTov4CsLA"},
    {"niche": "Cash City Picks", "master_title": "Cash City VIP", "src_bot": "user_HVCjzjUye5q5I", "src_comp": "biz_IR9QwwEFeC199z"},
    {"niche": "Deal Gains", "master_title": "Deal Gains Pass", "src_bot": "user_PUpL8cbyE1Zf2", "src_comp": "biz_62x0KF1HwUkUd2"},
    {"niche": "Deal Soldier", "master_title": "Deal Soldier Hub", "src_bot": "user_mnR4EbynVY8UA", "src_comp": "biz_Epy3Gq1LkscDbI"},
    {"niche": "Poke Alerts", "master_title": "Poke Alerts Hub", "src_bot": "user_VXlrbVwms4laY", "src_comp": "biz_3wuSbLPNZb4mU7"},
    {"niche": "Crystal Academy Hub", "master_title": "Crystal Academy Hub", "src_bot": "user_lMrwnvtkSSp6w", "src_comp": "biz_wIrZm2C9eZmsFB"},
    {"niche": "Official Picks VIP", "master_title": "Official Picks Pass", "src_bot": "user_pdd7UFzVXqlg4", "src_comp": "biz_06H1NGZWgkCioO"}
]

for b in BENCHMARKS:
    cdir = os.path.join(bots_dir, b["src_bot"], b["src_comp"])
    fsettings = os.path.join(cdir, "forum_settings.json")
    ssettings = os.path.join(cdir, "scheduler_settings.json")
    instr = os.path.join(cdir, "chatbot_instructions.md")
    
    f_ok = os.path.exists(fsettings)
    s_ok = os.path.exists(ssettings)
    i_ok = os.path.exists(instr)
    
    # Also check how many secondary communities this source bot has to see if we can reuse its secondary titles!
    bot_dir = os.path.join(bots_dir, b["src_bot"])
    secondaries = [d for d in os.listdir(bot_dir) if d != b["src_comp"] and os.path.isdir(os.path.join(bot_dir, d))]
    
    sec_titles = []
    for sc in secondaries:
        sc_cjson = os.path.join(bot_dir, sc, "company.json")
        if os.path.exists(sc_cjson):
            try:
                cname = json.load(open(sc_cjson, encoding="utf-8")).get("company_name")
                if cname:
                    sec_titles.append(cname)
            except:
                pass
                
    print(f"[{b['niche']}] Master: '{b['master_title']}' | Forum: {f_ok}, Sched: {s_ok}, Instr: {i_ok} | Extracted {len(sec_titles)} secondary titles")
