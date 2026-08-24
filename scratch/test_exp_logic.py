import os
import json
import time

bot_user_id = "user_lO14mFc5tBKN3"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pfile = os.path.join(base_dir, "profiles", "bots", bot_user_id, "profile.json")

with open(pfile, "r") as f:
    pdata = json.load(f)

token = pdata.get("oauth_token")

# Check token expiration
import base64
def is_token_expired(t):
    if not t: return True
    try:
        parts = t.split(".")
        if len(parts) != 3: return True
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.b64decode(payload).decode("utf-8"))
        exp = data.get("exp", 0)
        return time.time() > (exp - 60)
    except Exception as e:
        print("Error checking token exp:", e)
        return True

print("Token expired check:", is_token_expired(token))
print("Current env WHOP_COMPANY_ID:", os.getenv("WHOP_COMPANY_ID"))
print("Current env WHOP_EXPERIENCE_ID:", os.getenv("WHOP_EXPERIENCE_ID"))
