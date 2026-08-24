import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from update_whop_avatar import update_whop_user_avatar
from whop_auth import get_fresh_token

# High quality professional portrait CDN images
PORTRAITS = {
    "user_05rY5QBeq8ijk": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80", # Charles (Male)
    "user_10OFFiQpee8TG": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80", # Stephanie (Female)
    "user_18jSAOo8ltw8C": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80", # Cruz (Male)
    "user_2V0GkjoLxAwJu": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80", # Stacy (Female)
    "user_2l57lo63rmPUZ": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80", # Fanny (Female)
    "user_4oTEZeXKrHIVw": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&auto=format&fit=crop&q=80", # Allen (Male)
    "user_5ruy2xniJSfON": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop&q=80", # Sonya (Female)
    "user_6sYkOfNNp99cV": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80"  # Annette (Female)
}

def normalize_avatars():
    for bot_id, img_url in PORTRAITS.items():
        print(f"\n[UPDATING AVATAR] Bot: {bot_id}...")
        token = get_fresh_token(bot_id)
        if not token:
            print(f"  [ERROR] No token for {bot_id}")
            continue
            
        try:
            res = update_whop_user_avatar(token, img_url)
            pic_url = res.get("profile_picture", {}).get("url")
            print(f"  [SUCCESS] Updated @{res.get('username')} -> {pic_url}")
            
            # Update local profile.json
            pjson_path = os.path.join(BASE_DIR, "profiles", "bots", bot_id, "profile.json")
            if os.path.exists(pjson_path):
                pdata = json.load(open(pjson_path, encoding="utf-8"))
                pdata["profile_picture"] = pic_url
                pdata["profile_picture_url"] = pic_url
                with open(pjson_path, "w", encoding="utf-8") as pf:
                    json.dump(pdata, pf, indent=2)
        except Exception as e:
            print(f"  [FAILED] Error updating {bot_id}: {e}")

if __name__ == "__main__":
    normalize_avatars()
