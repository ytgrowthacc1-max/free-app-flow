import os
import json
import sys

sys.path.insert(0, "execution")
from whop_auth import get_fresh_token

bot_id = "user_gAkQk98I3AyP4"
print(f"Attempting token refresh for bot {bot_id} (@donnajacksona7)...")

# Clear the stale invalid flag first
pfile = f"profiles/bots/{bot_id}/profile.json"
with open(pfile, "r", encoding="utf-8") as f:
    data = json.load(f)
data["refresh_token_invalid"] = False
with open(pfile, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

token = get_fresh_token(bot_id)
if token:
    print(f"SUCCESS! Fresh token obtained for @donnajacksona7: {token[:20]}...")
else:
    print("FAILED to refresh token for @donnajacksona7.")
