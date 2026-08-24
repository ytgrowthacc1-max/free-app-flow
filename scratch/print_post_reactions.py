import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from dashboard_server import app

client = app.test_client()
response = client.get('/api/forum_analytics')
if response.status_code == 200:
    posts = response.json.get('posts', [])
    for p in posts:
        if p.get('emoji_reactions') or p.get('like_count', 0) > 0 or p.get('poll_reaction_count', 0) > 0:
            print(f"Title: {p.get('title')}")
            print(f"  Likes (like_count): {p.get('like_count')}")
            print(f"  Emoji reactions: {p.get('emoji_reactions')}")
            print(f"  Poll reaction count: {p.get('poll_reaction_count')}")
            print(f"  Poll votes: {p.get('poll_votes')}")
            print("-" * 40)
