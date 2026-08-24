import os
import json
import requests

bots_dir = "profiles/bots"
url = "https://api.whop.com/api/v1/companies"
payload = {
    "title": "Leaderboard App Community",
    "description": "Community promoting the Leaderboard application",
    "send_customer_emails": False
}

for bot_id in os.listdir(bots_dir):
    bot_path = os.path.join(bots_dir, bot_id)
    profile_file = os.path.join(bot_path, "profile.json")
    if os.path.isfile(profile_file):
        try:
            with open(profile_file, "r") as f:
                data = json.load(f)
            token = data.get("oauth_token") or data.get("whop_access_token")
            username = data.get("bot_username") or data.get("username", bot_id)
            if token:
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                res = requests.post(url, json=payload, headers=headers)
                print(f"User: {username} ({bot_id}) | Status: {res.status_code} | Msg: {res.text[:120]}")
        except Exception as e:
            pass
