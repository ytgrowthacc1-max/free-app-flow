import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WHOP_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

bots_dir = os.path.join("profiles", "bots")
for bot_id in os.listdir(bots_dir):
    bot_path = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bot_path):
        continue
    
    pfile = os.path.join(bot_path, "profile.json")
    bot_token = api_key
    if os.path.exists(pfile):
        try:
            with open(pfile, "r", encoding="utf-8") as pf:
                pdata = json.load(pf)
                if pdata.get("oauth_token"):
                    bot_token = pdata["oauth_token"]
        except Exception:
            pass

    for cid in os.listdir(bot_path):
        cpath = os.path.join(bot_path, cid)
        cfile = os.path.join(cpath, "company.json")
        if os.path.exists(cfile):
            with open(cfile, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            
            comp_id = cdata.get("company_id") or cid
            req_headers = {"Authorization": f"Bearer {bot_token}", "Content-Type": "application/json"}
            resp = requests.get(f"https://api.whop.com/api/v1/companies/{comp_id}", headers=req_headers)
            if resp.status_code != 200 and bot_token != api_key:
                resp = requests.get(f"https://api.whop.com/api/v1/companies/{comp_id}", headers=headers)
                
            if resp.status_code == 200:
                data = resp.json()
                route = data.get("route") or data.get("slug")
                if route:
                    route = route.strip('/')
                    cdata["route"] = route
                    cdata["whop_url"] = f"https://whop.com/joined/{route}/"
                    with open(cfile, "w", encoding="utf-8") as f:
                        json.dump(cdata, f, indent=2)
                    print(f"Updated {cfile}: route={route}, whop_url={cdata['whop_url']}")
            else:
                print(f"Failed to fetch {comp_id} (status {resp.status_code}): {resp.text[:100]}")
