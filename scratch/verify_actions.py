import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
from execution.whop_auth import get_fresh_token

token = get_fresh_token()
headers = {'Authorization': f'Bearer {token}'}

# Check comments under the post post_1Cc8HYphqiMJc5NKqLhKxQ
parent_id = "post_1Cc8HYphqiMJc5NKqLhKxQ"
comments_url = f"https://api.whop.com/api/v1/forum_posts?experience_id=exp_RpQSciawxkuJlm&parent_id={parent_id}"
r_comm = requests.get(comments_url, headers=headers)
if r_comm.status_code == 200:
    comms = r_comm.json()
    if isinstance(comms, dict):
        comms = comms.get('data', [])
    print(f"Comments found under this post: {len(comms)}")
    for idx, c in enumerate(comms):
        print(f"  Comment {idx+1}:")
        print(f"  ID: {c['id']}")
        print(f"  Content: {c['content']}")
        print(f"  Likes: {c.get('like_count', 0)}")
else:
    print("Error fetching comments:", r_comm.status_code, r_comm.text)
