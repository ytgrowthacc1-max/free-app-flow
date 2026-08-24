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
    data = response.json
    posts = data.get('posts', [])
    print(f"Total posts returned: {len(posts)}")
    
    id_counts = {}
    for p in posts:
        pid = p['id']
        id_counts[pid] = id_counts.get(pid, 0) + 1
        
    duplicates = {pid: count for pid, count in id_counts.items() if count > 1}
    print(f"Number of unique post IDs: {len(id_counts)}")
    print(f"Number of duplicate post IDs: {len(duplicates)}")
    if duplicates:
        print("Sample duplicates (ID: count):")
        for pid in list(duplicates.keys())[:5]:
            print(f"  {pid}: {duplicates[pid]}")
else:
    print("Error:", response.text)
