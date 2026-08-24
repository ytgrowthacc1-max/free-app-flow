import sys
import json
sys.path.append('execution')
from whop_auth import get_fresh_token

bot_user_id = "user_fdWsHxrBCGa62"

pfile = f"profiles/bots/{bot_user_id}/profile.json"
with open(pfile, "r", encoding="utf-8") as f:
    pdata = json.load(f)

print("Before test:")
print(f"  refresh_token_invalid: {pdata.get('refresh_token_invalid')}")
print(f"  oauth_token: {pdata.get('oauth_token')[:15]}...")
print(f"  refresh_token: {pdata.get('refresh_token')[:15]}...")

try:
    token = get_fresh_token(bot_user_id)
    print(f"\nSUCCESS! Fresh token obtained: {token[:15]}...")
    
    # Reload profile.json
    with open(pfile, "r", encoding="utf-8") as f:
        pdata2 = json.load(f)
    print("After get_fresh_token:")
    print(f"  refresh_token_invalid: {pdata2.get('refresh_token_invalid')}")
except Exception as e:
    print(f"\nFAILED to refresh token for {bot_user_id}: {e}")
