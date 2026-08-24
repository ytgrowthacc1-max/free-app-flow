import os
import json

profiles_dir = "profiles"
if os.path.exists(profiles_dir):
    for slug in os.listdir(profiles_dir):
        p_dir = os.path.join(profiles_dir, slug)
        if os.path.isdir(p_dir):
            p_json_path = os.path.join(p_dir, "profile.json")
            if os.path.exists(p_json_path):
                with open(p_json_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        print(f"=== Profile: {slug} ===")
                        print(f"  Company Name:  {data.get('company_name')}")
                        print(f"  Company ID:    {data.get('company_id')}")
                        print(f"  Bot User ID:   {data.get('bot_user_id')}")
                    except Exception as e:
                        print(f"  Error reading {p_json_path}: {e}")
            else:
                print(f"=== Profile: {slug} (No profile.json) ===")
else:
    print("profiles directory not found")
