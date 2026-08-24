import os
import json
import requests

bot_user_id = "user_lO14mFc5tBKN3"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pfile = os.path.join(base_dir, "profiles", "bots", bot_user_id, "profile.json")

with open(pfile, "r") as f:
    pdata = json.load(f)

token = pdata.get("oauth_token")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Fetch experiences for XP Arena
r_comp = requests.get("https://api.whop.com/api/v1/experiences?company_id=biz_pV1MfpPbaGydou", headers=headers)
exps = r_comp.json().get("data", [])

print("--- EXPERIENCES UNDER XP ARENA ---")
for e in exps:
    print(f"ID: {e['id']} | Name: {e['name']} | App: {e['app']['name']} | is_public: {e['is_public']}")

print("\n--- POSTS PER FORUM EXPERIENCE ---")
for e in exps:
    if e['app']['name'] == "Forums":
        exp_id = e['id']
        r_posts = requests.get(f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&limit=50", headers=headers)
        if r_posts.status_code == 200:
            posts = r_posts.json().get("data", [])
            print(f"\nExperience: '{e['name']}' ({exp_id}) | is_public={e['is_public']} -> Found {len(posts)} posts:")
            for p in posts:
                title = p.get('title', '') or ''
                print(f"  - Post ID: {p.get('id')}, parent_id: {p.get('parent_id')}, title: {title.encode('ascii', 'replace').decode()}")
