import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
app_id = "app_tHhlowWfWKDkIF"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Step 1: List user companies via GET /v1/companies or /v2/companies
print("--- STEP 1: Fetching companies for @dawnmuros ---")
comp_res = requests.get("https://api.whop.com/v1/companies", headers=headers)
print("Companies status:", comp_res.status_code)
print("Companies text:", comp_res.text[:500])

company_id = None
if comp_res.status_code == 200:
    c_data = comp_res.json().get("data", [])
    if c_data:
        company_id = c_data[0].get("id")
        print(f"[INFO] Found {len(c_data)} companies. Selected first company: {company_id} ({c_data[0].get('title')})")

if not company_id:
    # Try fetching company from dashboard profiles/ database if API list empty
    import sqlite3
    db_path = r"C:\Python\Browsing Skill Agent\scratch\..\profiles.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT companies FROM profiles WHERE account_number = 54")
        row = cur.fetchone()
        if row and row[0]:
            comps = json.loads(row[0])
            if comps:
                company_id = comps[0].get("id")
                print(f"[INFO] Found company from DB: {company_id} ({comps[0].get('title')})")

if not company_id:
    print("[ERROR] Could not find any company ID for @dawnmuros.")
    sys.exit(1)

# Step 2: Create experience POST /v1/experiences or POST /api/v1/experiences
print(f"\n--- STEP 2: Installing app {app_id} for company {company_id} ---")
endpoints = [
    "https://api.whop.com/api/v1/experiences",
    "https://api.whop.com/v1/experiences"
]

for url in endpoints:
    exp_res = requests.post(
        url,
        headers=headers,
        json={
            "app_id": app_id,
            "company_id": company_id
        }
    )
    print(f"URL: {url} | Status: {exp_res.status_code} | Text: {exp_res.text[:500]}")
    if exp_res.status_code in (200, 201):
        print("\n=======================================================")
        print(f"🎉 SUCCESS! INSTALLED APP {app_id} TO COMPANY {company_id}!")
        print("=======================================================")
        break
