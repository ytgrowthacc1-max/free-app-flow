import sys
sys.path.append('execution')
import pending_db

posts = pending_db.get_pending_posts()
print(f"Total pending posts: {len(posts)}")
for p in posts:
    print("\n----------------------------------------")
    print(f"ID: {p.get('id')}")
    print(f"Profile / Company ID: {p.get('profile_id')} / {p.get('company_id')}")
    print(f"Title: {p.get('title')}")
    print(f"Status: {p.get('status')}")
    print(f"Post Type: {p.get('post_type')}")
    print(f"Scheduled Time: {p.get('scheduled_at')}")
    print(f"Created At: {p.get('created_at')}")
    print(f"Error: {p.get('error')}")
