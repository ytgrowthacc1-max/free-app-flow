import os
import glob
import json

base_dir = "profiles"
fixed_count = 0

for root, dirs, files in os.walk(base_dir):
    if "profile.json" in files:
        pf = os.path.join(root, "profile.json")
        try:
            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if data.get("refresh_token_invalid"):
                uname = data.get("bot_username") or data.get("username") or root
                print(f"Found stale refresh_token_invalid: True in {pf} (User: {uname})")
                data.pop("refresh_token_invalid", None)
                data.pop("error_message", None)
                with open(pf, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                fixed_count += 1
                print(f"  --> Cleared refresh_token_invalid flag for {uname}!")
        except Exception as e:
            print(f"Error {pf}: {e}")

print(f"\nTotal stale credential flags cleared: {fixed_count}")
