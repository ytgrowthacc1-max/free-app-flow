import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

if not os.path.exists(bots_dir):
    print("No profiles/bots directory found.")
    exit()

bot_folders = [f for f in os.listdir(bots_dir) if os.path.isdir(os.path.join(bots_dir, f))]

zero_community_bots = []
with_community_bots = []

for bot_id in bot_folders:
    bpath = os.path.join(bots_dir, bot_id)
    pfile = os.path.join(bpath, "profile.json")
    
    bot_username = "unknown"
    email = "unknown"
    if os.path.exists(pfile):
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                data = json.load(f)
                bot_username = data.get("bot_username") or data.get("username") or "unknown"
                email = data.get("email") or "unknown"
        except Exception:
            pass
            
    # Check for subdirectories (companies)
    subdirs = [d for d in os.listdir(bpath) if os.path.isdir(os.path.join(bpath, d))]
    
    if len(subdirs) == 0:
        zero_community_bots.append({
            "bot_user_id": bot_id,
            "bot_username": bot_username,
            "email": email
        })
    else:
        with_community_bots.append({
            "bot_user_id": bot_id,
            "bot_username": bot_username,
            "communities_count": len(subdirs)
        })

print(f"Total Dashboard Bot Fleet: {len(bot_folders)}")
print(f"Bots WITH Communities: {len(with_community_bots)}")
print(f"Bots WITH 0 Communities: {len(zero_community_bots)}")
print("\n--- List of Bots with 0 Communities ---")
for idx, bot in enumerate(zero_community_bots, 1):
    print(f"{idx}. @{bot['bot_username']} ({bot['bot_user_id']}) | Email: {bot['email']}")
