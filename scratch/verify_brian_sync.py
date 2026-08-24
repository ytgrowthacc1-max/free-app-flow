import os
import json
import requests

def main():
    pfile = r"profiles/bots/user_7ziL4hNckh6Ei/profile.json"
    if not os.path.exists(pfile):
        print("Profile file not found!")
        return
        
    with open(pfile, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    token = data.get("oauth_token")
    if not token:
        print("OAuth token is empty!")
        return
        
    print("Querying Whop API /companies using briandelgadillo's fresh token...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("https://api.whop.com/api/v1/companies", headers=headers, timeout=15)
    
    print("Response status code:", resp.status_code)
    if resp.status_code == 200:
        companies = resp.json().get("data", [])
        print(f"Successfully retrieved {len(companies)} companies:")
        for comp in companies:
            print(f"- Name: {comp.get('title') or comp.get('name')}, ID: {comp.get('id')}")
    else:
        print("Failed to fetch companies:", resp.text)

if __name__ == "__main__":
    main()
