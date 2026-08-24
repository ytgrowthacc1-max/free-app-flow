import sys
import os
import sqlite3

base_dir = r"c:\Python\Browsing Skill Agent"
sys.path.append(os.path.join(base_dir, "execution"))

import profile_db as db

profiles = db.list_profiles(platform="whop")
print(f"Total whop profiles found: {len(profiles)}")

found = False
for p in profiles:
    # Print some info
    pname = p.get("name", "")
    pnum = p.get("account_number")
    # Let's read extra details if any
    print(f"Account #{pnum}: Email={pname}, ID={p.get('id')}, Status={p.get('status')}")
    if "briandelgadillo" in pname.lower() or "brian" in pname.lower():
        print("--> MATCH FOUND!")
        found = True

if not found:
    print("No direct username match for brian. Checking all entries...")
