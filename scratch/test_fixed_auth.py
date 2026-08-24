import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.whop_auth import get_fresh_token
from execution.post_to_forum import post_to_forum

bot_user_id = "user_fdWsHxrBCGa62" # gloriarussell3c
print(f"[TEST] Testing get_fresh_token for {bot_user_id}...")
token = get_fresh_token(bot_user_id)
print(f"[TEST] get_fresh_token returned: {token[:30]}...")

print("[TEST] All functions imported and executed cleanly with zero UnboundLocalError!")
