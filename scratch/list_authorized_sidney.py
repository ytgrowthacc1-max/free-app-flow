import os
import requests
import json

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def main():
    profile_path = "profiles/bots/user_JPHEqzhggecW9/profile.json"
    if not os.path.exists(profile_path):
        print("[ERROR] Profile not found")
        return
        
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        token = data.get("oauth_token")
        
    url = "https://api.whop.com/api/v1/authorized_users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "company_id": "biz_R3lCX4ljztxERk"
    }
    
    print("[INFO] Querying /authorized_users with sidneysanders61 token...")
    resp = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        safe_print(json.dumps(resp.json(), indent=2))
    else:
        safe_print(resp.text)

if __name__ == "__main__":
    main()
