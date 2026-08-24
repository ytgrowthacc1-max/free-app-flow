import os
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

TARGET_10 = [
    {"bot_id": "user_05rY5QBeq8ijk", "username": "charlespeachey", "niche": "Revenue Apps", "master_title": "Revenue Apps VIP", "src_bot": "user_eSN5Z4XrLT0ZQ", "src_comp": "biz_VHlv37S71ESE1G"},
    {"bot_id": "user_0Ll0BPufaOuQZ", "username": "estellalynch", "niche": "XP Arena", "master_title": "XP Arena VIP", "src_bot": "user_lO14mFc5tBKN3", "src_comp": "biz_pV1MfpPbaGydou"},
    {"bot_id": "user_10OFFiQpee8TG", "username": "stephanieabrego", "niche": "The Tools Pack", "master_title": "The Tools Pack VIP", "src_bot": "user_UCUWNo0s132ET", "src_comp": "biz_c9ai0lCMJoCw9e"},
    {"bot_id": "user_18jSAOo8ltw8C", "username": "cruzsaylors", "niche": "Flip Empire", "master_title": "Flip Empire VIP", "src_bot": "user_puyTsi9E4vLkP", "src_comp": "biz_LK1qoXTov4CsLA"},
    {"bot_id": "user_2V0GkjoLxAwJu", "username": "stacycollins", "niche": "Cash City Picks", "master_title": "Cash City VIP", "src_bot": "user_HVCjzjUye5q5I", "src_comp": "biz_IR9QwwEFeC199z"},
    {"bot_id": "user_2l57lo63rmPUZ", "username": "fannystrickland", "niche": "Deal Gains", "master_title": "Deal Gains Pass", "src_bot": "user_PUpL8cbyE1Zf2", "src_comp": "biz_62x0KF1HwUkUd2"},
    {"bot_id": "user_4oTEZeXKrHIVw", "username": "allenbakerdb", "niche": "Deal Soldier", "master_title": "Deal Soldier Hub", "src_bot": "user_mnR4EbynVY8UA", "src_comp": "biz_Epy3Gq1LkscDbI"},
    {"bot_id": "user_5ruy2xniJSfON", "username": "sonyahoworth", "niche": "Poke Alerts", "master_title": "Poke Alerts Hub", "src_bot": "user_VXlrbVwms4laY", "src_comp": "biz_3wuSbLPNZb4mU7"},
    {"bot_id": "user_6UbnHssZpNyZT", "username": "billieealey", "niche": "Crystal Academy Hub", "master_title": "Crystal Academy Hub", "src_bot": "user_lMrwnvtkSSp6w", "src_comp": "biz_wIrZm2C9eZmsFB"},
    {"bot_id": "user_6sYkOfNNp99cV", "username": "annettegilbert", "niche": "Official Picks VIP", "master_title": "Official Picks Pass", "src_bot": "user_pdd7UFzVXqlg4", "src_comp": "biz_06H1NGZWgkCioO"}
]

print("Verifying 10 fresh target bots:")
for t in TARGET_10:
    bpath = os.path.join(bots_dir, t["bot_id"])
    subdirs = [d for d in os.listdir(bpath) if os.path.isdir(os.path.join(bpath, d)) and (d.startswith("biz_") or d.startswith("comp_"))]
    print(f"  {t['bot_id']} (@{t['username']}) -> Communities on disk: {len(subdirs)} | Assigned Niche: {t['niche']}")
