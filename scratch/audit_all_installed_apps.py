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

# Fetch companies
comp_res = requests.get("https://api.whop.com/v1/companies", headers=headers)
companies = comp_res.json().get("data", []) if comp_res.status_code == 200 else []

installed_companies = []
uninstalled_companies = []

print(f"[AUDIT] Scanning {len(companies)} companies for app {target_app_id}...\n")

for c in companies:
    c_id = c.get("id")
    c_title = c.get("title")
    
    url = f"https://api.whop.com/v1/experiences?company_id={c_id}"
    exp_res = requests.get(url, headers=headers)
    
    has_app = False
    app_exp_id = None
    if exp_res.status_code == 200:
        exps = exp_res.json().get("data", [])
        for exp in exps:
            app_id = exp.get("app", {}).get("id")
            if app_id == target_app_id:
                has_app = True
                app_exp_id = exp.get("id")
                break

    if has_app:
        installed_companies.append({"id": c_id, "title": c_title, "exp_id": app_exp_id})
        print(f" [INSTALLED]   : {c_title:<35} | Company ID: {c_id} | Exp ID: {app_exp_id}")
    else:
        uninstalled_companies.append({"id": c_id, "title": c_title})
        print(f" [UNINSTALLED] : {c_title:<35} | Company ID: {c_id}")

print("\n=========================================================================")
print(f"SUMMARY FOR APP {target_app_id}:")
print(f"   Installed   : {len(installed_companies)} / {len(companies)}")
print(f"   Uninstalled : {len(uninstalled_companies)} / {len(companies)}")
print("=========================================================================")
