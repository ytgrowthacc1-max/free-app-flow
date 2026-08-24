import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from whop_auth import auto_authorize_bot_profile, get_fresh_token

bot_id = "user_6sYkOfNNp99cV"

# Try auto authorization with camoufox / cloakbrowser
print(f"Auto-authorizing {bot_id}...")
res = auto_authorize_bot_profile(bot_id)
print(f"Auto auth result: {res}")
