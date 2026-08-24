import os
import glob
import json

base = "profiles"
for root, dirs, files in os.walk(base):
    if "profile.json" in files:
        pf = os.path.join(root, "profile.json")
        try:
            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)
            uname = data.get("bot_username") or data.get("username") or data.get("name")
            if "gloria" in str(uname).lower() or "cash" in str(root).lower() or "betting" in str(root).lower():
                print(f"Profile File: {pf}")
                print(f"  Keys: {list(data.keys())}")
                print(f"  username: {uname}")
                print(f"  refresh_token_invalid: {data.get('refresh_token_invalid')}")
                print(f"  has oauth_token: {bool(data.get('oauth_token'))}")
                print(f"  has refresh_token: {bool(data.get('refresh_token'))}")
                print(f"  error_message: {data.get('error_message')}")
        except Exception as e:
            print(f"Error {pf}: {e}")
