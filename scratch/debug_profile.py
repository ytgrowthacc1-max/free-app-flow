import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))

company_id = os.getenv("WHOP_COMPANY_ID", "")
print("WHOP_COMPANY_ID:", repr(company_id))

profiles_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profiles")
print("PROFILES_DIR:", profiles_dir)
print("EXISTS:", os.path.exists(profiles_dir))
if os.path.exists(profiles_dir):
    print("LIST:", os.listdir(profiles_dir))
    for slug in os.listdir(profiles_dir):
        pfile = os.path.join(profiles_dir, slug, "profile.json")
        print("PFILE:", pfile, "EXISTS:", os.path.exists(pfile))
        if os.path.exists(pfile):
            with open(pfile, "r", encoding="utf-8") as f:
                pdata = json.load(f)
            print("  DATA:", pdata)
            print("  MATCH:", pdata.get("company_id") == company_id)
