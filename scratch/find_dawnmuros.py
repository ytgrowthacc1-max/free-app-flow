import os
import json

profiles_dir = r".\profiles\bots"
for folder in os.listdir(profiles_dir):
    p_file = os.path.join(profiles_dir, folder, "profile.json")
    if os.path.exists(p_file):
        try:
            with open(p_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "dawnmuros" in json.dumps(data).lower():
                    print(f"Found dawnmuros in {folder}: username={data.get('bot_username')}, id={data.get('bot_user_id')}")
                    print("Keys:", list(data.keys()))
                    if "access_token" in data:
                        print("access_token:", data["access_token"][:20])
                    if "oauth" in data:
                        print("oauth:", data["oauth"])
        except Exception as e:
            print("Error:", e)
