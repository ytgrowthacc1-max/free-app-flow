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

urls = [
    "https://api.whop.com/api/v5/files",
    "https://api.whop.com/v5/files",
    "https://api.whop.com/api/v2/files",
    "https://api.whop.com/v2/files"
]

header_options = [
    {"Authorization": f"Bearer {token}"},
    {"Authorization": f"Bearer {company_api_key}"},
    {"x-api-key": company_api_key},
    {"x-whop-api-key": company_api_key}
]

payload = {"filename": "avatar.jpg", "visibility": "public"}

for url in urls:
    for h in header_options:
        h_copy = h.copy()
        h_copy["Content-Type"] = "application/json"
        r = requests.post(url, headers=h_copy, json=payload)
        if r.status_code != 404:
            print(f"URL: {url} | Header: {list(h.keys())[0]} | Status: {r.status_code} | Text: {r.text[:300]}")
