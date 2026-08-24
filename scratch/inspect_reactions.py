import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'execution'))
from whop_auth import get_fresh_token

load_dotenv()
bot_user_id = os.getenv('BOT_USER_ID')
token = get_fresh_token(bot_user_id)
headers = {'Authorization': f'Bearer {token}'}
exp_id = os.getenv('WHOP_EXPERIENCE_ID')

print(f"Fetching posts for experience: {exp_id}...", flush=True)
url = f'https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&limit=15'
r = requests.get(url, headers=headers)
if r.status_code != 200:
    print(f"Failed to fetch posts: {r.status_code} - {r.text}", flush=True)
    sys.exit(1)

posts = [p for p in r.json().get('data', []) if not p.get('parent_id')]
print(f"Found {len(posts)} top-level posts.", flush=True)

for p in posts[:12]:
    pid = p['id']
    title = p.get('title', 'Untitled')
    
    # Fetch detail
    detail_r = requests.get(f'https://api.whop.com/api/v1/forum_posts/{pid}', headers=headers)
    detail_data = detail_r.json() if detail_r.status_code == 200 else {}
    
    # Fetch reactions
    rx_r = requests.get(f'https://api.whop.com/api/v1/reactions?resource_id={pid}', headers=headers)
    rx_data = rx_r.json().get('data', []) if rx_r.status_code == 200 else []
    
    print("\n--------------------------------------------------", flush=True)
    print(f"POST: {pid} | Title: {title}", flush=True)
    print(f"Detail keys: {list(detail_data.keys())}", flush=True)
    if 'poll' in detail_data and detail_data['poll']:
        print("  [POLL FIELD FOUND IN DETAIL!]", flush=True)
        print(json.dumps(detail_data['poll'], indent=2), flush=True)
    else:
        print("  No poll field in detail.", flush=True)
        
    print(f"Reactions count: {len(rx_data)}", flush=True)
    for rx in rx_data:
        print(f"  - React ID: {rx.get('id')}", flush=True)
        print(f"    User: {rx.get('user', {}).get('username')} ({rx.get('user', {}).get('id')})", flush=True)
        print(f"    Emoji: {repr(rx.get('emoji'))}", flush=True)
        print(f"    Poll Option ID: {rx.get('poll_option_id')}", flush=True)
        print(f"    Full Reaction: {json.dumps(rx)}", flush=True)

