import os
import json
import shutil
import requests
from dotenv import load_dotenv

load_dotenv()

# We need to load user_7ziL4hNckh6Ei (briandelgadillo) profile
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
brian_id = "user_7ziL4hNckh6Ei"
eric_id = "user_QuVGhaKJDTJyi"
company_id = "biz_g3xtLNhhkuw2dD"

brian_profile_path = os.path.join(base_dir, "profiles", "bots", brian_id, "profile.json")

if not os.path.exists(brian_profile_path):
    print(f"Error: Profile for @briandelgadillo not found at {brian_profile_path}")
    exit(1)

with open(brian_profile_path, "r", encoding="utf-8") as f:
    brian_data = json.load(f)

access_token = brian_data.get("oauth_token")
refresh_token = brian_data.get("refresh_token")
bot_username = brian_data.get("bot_username", "briandelgadillo")

# Fetch companies for brian
headers = {"Authorization": f"Bearer {access_token}"}
print("Fetching companies for @briandelgadillo...")
r = requests.get("https://api.whop.com/api/v1/companies", headers=headers)
if r.status_code != 200:
    print(f"Failed to fetch companies: {r.status_code} - {r.text}")
    # Try refreshing token first in case it's expired
    print("Attempting to refresh brian's token...")
    client_id = os.getenv("WHOP_APP_ID")
    client_secret = os.getenv("WHOP_API_KEY")
    token_url = "https://api.whop.com/oauth/token"
    token_payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    tr = requests.post(token_url, json=token_payload)
    if tr.status_code == 200:
        tdata = tr.json()
        access_token = tdata.get("access_token")
        refresh_token = tdata.get("refresh_token")
        brian_data["oauth_token"] = access_token
        brian_data["refresh_token"] = refresh_token
        with open(brian_profile_path, "w", encoding="utf-8") as wf:
            json.dump(brian_data, wf, indent=2)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get("https://api.whop.com/api/v1/companies", headers=headers)
        if r.status_code != 200:
            print(f"Failed to fetch companies after refresh: {r.status_code} - {r.text}")
            exit(1)
    else:
        print(f"Refresh failed: {tr.status_code} - {tr.text}")
        exit(1)

companies = r.json().get("data", [])
print(f"Found companies: {[c.get('name') or c.get('title') for c in companies]}")

# Import bot and companies for brian
# Since we want to reproduce the behavior of import_bot_and_companies in dashboard_server.py:
bot_dir = os.path.dirname(brian_profile_path)
os.makedirs(bot_dir, exist_ok=True)

# 1. Update brian's profile.json
brian_data["oauth_token"] = access_token
brian_data["refresh_token"] = refresh_token
with open(brian_profile_path, "w", encoding="utf-8") as f:
    json.dump(brian_data, f, indent=2)

# 2. Setup each company directory
for comp in companies:
    comp_id = comp.get("id")
    comp_name = comp.get("title") or comp.get("name") or comp_id
    if not comp_id:
        continue
        
    comp_dir = os.path.join(bot_dir, comp_id)
    os.makedirs(comp_dir, exist_ok=True)
    
    comp_pfile = os.path.join(comp_dir, "company.json")
    experience_id = None
    
    # Query Whop API for experiences
    try:
        exp_resp = requests.get(f"https://api.whop.com/api/v1/experiences?company_id={comp_id}", headers=headers, timeout=5)
        if exp_resp.status_code == 200:
            exps = exp_resp.json().get("data", [])
            for exp in exps:
                app_info = exp.get("app", {})
                if app_info.get("id") == "app_dYfm2IdXhDMquv" or app_info.get("name") == "Forums":
                    experience_id = exp.get("id")
                    break
    except Exception as e:
        print(f"Error fetching experiences: {e}")
        
    comp_pdata = {
        "company_id": comp_id,
        "company_name": comp_name,
        "experience_id": experience_id or "",
        "hidden": False
    }
    with open(comp_pfile, "w", encoding="utf-8") as f:
        json.dump(comp_pdata, f, indent=2)
    print(f"Set up company {comp_name} ({comp_id}) with experience {experience_id} for @briandelgadillo")

# Copy settings from @ericdavis8b (user_QuVGhaKJDTJyi) to @briandelgadillo (user_7ziL4hNckh6Ei) for tools bundle (biz_g3xtLNhhkuw2dD)
eric_comp_dir = os.path.join(base_dir, "profiles", "bots", eric_id, company_id)
brian_comp_dir = os.path.join(base_dir, "profiles", "bots", brian_id, company_id)

if os.path.exists(eric_comp_dir):
    os.makedirs(brian_comp_dir, exist_ok=True)
    for fname in ["scheduler_settings.json", "chatbot_settings.json", "chatbot_instructions.md"]:
        src = os.path.join(eric_comp_dir, fname)
        dst = os.path.join(brian_comp_dir, fname)
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"Copied {fname} from @ericdavis8b to @briandelgadillo")
        else:
            print(f"Warning: {fname} not found in @ericdavis8b settings")
else:
    print(f"Error: @ericdavis8b settings directory not found at {eric_comp_dir}")
