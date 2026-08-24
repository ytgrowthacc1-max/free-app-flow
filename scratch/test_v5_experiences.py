import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

target_app_id = "app_tHhlowWfWKDkIF"
test_biz_id = "biz_pV1MfpPbaGydou" # XP Arena

endpoints = [
    f"https://api.whop.com/api/v5/companies/{test_biz_id}/experiences",
    f"https://api.whop.com/v5/companies/{test_biz_id}/experiences",
    f"https://api.whop.com/api/v2/companies/{test_biz_id}/experiences",
    f"https://api.whop.com/v1/experiences?company_id={test_biz_id}",
    f"https://api.whop.com/api/v1/experiences?company_id={test_biz_id}"
]

for url in endpoints:
    res = requests.get(url, headers=headers)
    print(f"URL: {url} | Status: {res.status_code} | Text: {res.text[:400]}")
