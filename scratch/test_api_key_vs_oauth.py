import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
company_api_key = os.getenv("WHOP_API_KEY")

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

user_oauth_token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

print("--- Test 1: v2 user update with Company API Key ---")
headers_company = {
    "Authorization": f"Bearer {company_api_key}",
    "Content-Type": "application/json"
}
r1 = requests.patch("https://api.whop.com/v2/users/user_lO14mFc5tBKN3", headers=headers_company, json={"profile_pic_url": avatar_url})
print("Company API Key (v2/users/user_lO14mFc5tBKN3):", r1.status_code, r1.text[:300])

r1_me = requests.patch("https://api.whop.com/v2/users/me", headers=headers_company, json={"profile_pic_url": avatar_url})
print("Company API Key (v2/users/me):", r1_me.status_code, r1_me.text[:300])

print("\n--- Test 2: v5 user update with User OAuth Token ---")
headers_user = {
    "Authorization": f"Bearer {user_oauth_token}",
    "Content-Type": "application/json"
}
r2 = requests.patch("https://api.whop.com/v2/users/user_lO14mFc5tBKN3", headers=headers_user, json={"profile_pic_url": avatar_url})
print("User OAuth (v2/users/user_lO14mFc5tBKN3):", r2.status_code, r2.text[:300])

r3 = requests.patch("https://api.whop.com/v2/users/me", headers=headers_user, json={"profile_pic_url": avatar_url})
print("User OAuth (v2/users/me):", r3.status_code, r3.text[:300])
