import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from auto_forum_poster import run_auto_poster

bot_id = "user_7TW5tuOsmnpOq"
master_cid = "biz_NVxgoFpMbXPl6u"
master_exp = "exp_HtI6xOMgG3go4J"

print(f"Testing auto_forum_poster on @stanleyrodrigueze2 ({master_cid}, {master_exp})...")
os.environ["BOT_USER_ID"] = bot_id
os.environ["WHOP_COMPANY_ID"] = master_cid
os.environ["WHOP_EXPERIENCE_ID"] = master_exp

res = run_auto_poster(draft_mode=False, experience_id=master_exp, bot_user_id=bot_id, return_post_details=True)
print(f"Result: {res}")
