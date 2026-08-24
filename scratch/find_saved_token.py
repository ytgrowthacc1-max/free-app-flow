import os
import json

base_dir = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles"
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".json"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8") as file:
                    content = file.read()
                    if "dawnmuros" in content or "user_lO14mFc5tBKN3" in content or "access_token" in content:
                        print("Found profile file:", p)
            except Exception:
                pass
