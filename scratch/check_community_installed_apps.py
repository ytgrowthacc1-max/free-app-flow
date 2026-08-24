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

# 1. Fetch companies
comp_res = requests.get("https://api.whop.com/v1/companies", headers=headers)
print("Companies status:", comp_res.status_code)

companies = comp_res.json().get("data", []) if comp_res.status_code == 200 else []
print(f"Total companies retrieved: {len(companies)}")

installed_companies = []
uninstalled_companies = []

for c in companies:
    c_id = c.get("id")
    c_title = c.get("title")
    
    # Check experiences for this company
    exp_res = requests.get(f"https://api.whop.com/v1/companies/{c_id}/experiences", headers=headers)
    
    has_app = False
    if exp_res.status_code == 200:
        exps = exp_res.json().get("data", [])
        for exp in exps:
            e_app_id = exp.get("app", {}).get("id")
            if e_app_id == target_app_id:
                has_app = True
                break
    else:
        # Fallback to GET /v1/experiences with company filter or query
        pass

    if has_app:
        installed_companies.append({"id": c_id, "title": c_title})
        print(f" [INSTALLED]  {c_title} ({c_id})")
    else:
        uninstalled_companies.append({"id": c_id, "title": c_title})
        print(f" [MISSING]    {c_title} ({c_id})")

print("\n=======================================================")
print(f"SUMMARY FOR APP {target_app_id}:")
print(f" Installed:   {len(installed_companies)} / {len(companies)}")
print(f" Uninstalled: {len(uninstalled_companies)} / {len(companies)}")
print("=======================================================")
