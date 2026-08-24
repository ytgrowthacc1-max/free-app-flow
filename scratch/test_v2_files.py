import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
company_api_key = os.getenv("WHOP_API_KEY")

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

access_token = data.get("oauth_token")

avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"
img_bytes = requests.get(avatar_url).content

print("--- Test 1: POST https://api.whop.com/v2/files with Company API Key ---")
r1 = requests.post(
    "https://api.whop.com/v2/files",
    headers={"Authorization": f"Bearer {company_api_key}"},
    files={"file": ("avatar.jpg", img_bytes, "image/jpeg")}
)
print("Status:", r1.status_code)
print("Text:", r1.text[:500])

print("\n--- Test 2: POST https://api.whop.com/v2/files with User OAuth Token ---")
r2 = requests.post(
    "https://api.whop.com/v2/files",
    headers={"Authorization": f"Bearer {access_token}"},
    files={"file": ("avatar.jpg", img_bytes, "image/jpeg")}
)
print("Status:", r2.status_code)
print("Text:", r2.text[:500])
