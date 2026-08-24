import os
import json
import requests

# Set environment variables for XP Arena
bot_user_id = "user_lO14mFc5tBKN3"
company_id = "biz_pV1MfpPbaGydou"

os.environ["BOT_USER_ID"] = bot_user_id
os.environ["WHOP_COMPANY_ID"] = company_id

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pfile = os.path.join(base_dir, "profiles", "bots", bot_user_id, "profile.json")

with open(pfile, "r") as f:
    pdata = json.load(f)

token = pdata.get("oauth_token")

# Call Whop API to get experiences
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
url = f"https://api.whop.com/api/v1/experiences?company_id={company_id}"
r = requests.get(url, headers=headers, timeout=10)

print("STATUS CODE:", r.status_code)
forums = []
if r.status_code == 200:
    data = r.json().get("data", [])
    for exp in data:
        app_info = exp.get("app", {})
        print(f"Exp: id={exp.get('id')}, name={exp.get('name')}, app_id={app_info.get('id')}, app_name={app_info.get('name')}")
        if app_info.get("id") == "app_dYfm2IdXhDMquv" or app_info.get("name") == "Forums":
            forums.append({
                "id": exp.get("id"),
                "name": exp.get("name")
            })

print("\nFILTERED FORUMS:", json.dumps(forums, indent=2))
