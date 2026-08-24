import json
import requests

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

app_id = "app_tHhlowWfWKDkIF"

# Fetch experiences from Whop API
res = requests.get("https://api.whop.com/v1/experiences", headers=headers)
print("Experiences status:", res.status_code)

installed_from_api = []
if res.status_code == 200:
    exp_list = res.json().get("data", [])
    for exp in exp_list:
        e_app_id = exp.get("app", {}).get("id")
        comp = exp.get("company", {})
        if e_app_id == app_id:
            installed_from_api.append({
                "experience_id": exp.get("id"),
                "company_id": comp.get("id"),
                "company_title": comp.get("title")
            })

print(f"\n[API RESULT] Found {len(installed_from_api)} installed experiences for app {app_id}:")
for item in installed_from_api:
    print(f" - {item['company_title']} ({item['company_id']}) -> Experience: {item['experience_id']}")
