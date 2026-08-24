import os
import sys
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
sys.path.append(os.path.join(os.getcwd(), 'execution'))
from whop_auth import get_fresh_token

bot_user_id = os.getenv("BOT_USER_ID")
token = get_fresh_token(bot_user_id) if bot_user_id else get_fresh_token()
exp_id = os.getenv("WHOP_EXPERIENCE_ID")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

all_posts = []
seen_ids = set()
cursor = None
limit = 50

for page_idx in range(1, 11):
    url = f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&limit={limit}"
    if cursor:
        url += f"&after={cursor}"
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f"[WARNING] GET failed: {r.status_code}")
        break
        
    res = r.json()
    data = res.get("data", [])
    if not data:
        break
        
    new_added = 0
    for p in data:
        pid = p.get("id")
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            all_posts.append(p)
            new_added += 1
            
    print(f"Page {page_idx}: fetched {len(data)}, new unique added: {new_added}")
    if new_added == 0:
        break
        
    page_info = res.get("page_info", {})
    if not page_info.get("has_next_page"):
        break
        
    cursor = page_info.get("end_cursor")
    if not cursor:
        break

print(f"Total unique posts fetched: {len(all_posts)}")
