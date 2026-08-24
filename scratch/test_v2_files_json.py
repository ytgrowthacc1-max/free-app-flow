import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
company_api_key = os.getenv("WHOP_API_KEY")

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

print("--- Test JSON payloads on v2/files ---")
payloads = [
    {"filename": "avatar.jpg", "visibility": "public"},
    {"url": avatar_url},
    {"file_url": avatar_url},
    {"image_url": avatar_url}
]

for p in payloads:
    r = requests.post(
        "https://api.whop.com/v2/files",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=p
    )
    print(f"Payload: {list(p.keys())[0]} | Status: {r.status_code} | Text: {r.text[:300]}")
