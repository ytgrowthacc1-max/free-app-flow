import sys
import os
import json
import re

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db

base_bots_dir = r"c:\Python\WHOP AUTOMATION AGENTIC\profiles\bots"

existing_bot_ids = set()
existing_usernames = set()
existing_emails = set()

if os.path.exists(base_bots_dir):
    for bfolder in os.listdir(base_bots_dir):
        existing_bot_ids.add(bfolder.lower())
        pfile = os.path.join(base_bots_dir, bfolder, "profile.json")
        if os.path.exists(pfile):
            try:
                with open(pfile, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("bot_user_id"):
                        existing_bot_ids.add(data["bot_user_id"].lower())
                    if data.get("bot_username"):
                        existing_usernames.add(data["bot_username"].lower())
                    if data.get("email"):
                        existing_emails.add(data["email"].lower())
            except Exception:
                pass

print(f"Existing Bot IDs in Dashboard: {len(existing_bot_ids)}")
print(f"Existing Usernames in Dashboard: {len(existing_usernames)}")
print(f"Existing Emails in Dashboard: {len(existing_emails)}")

whop_profiles = db.list_profiles(platform="whop")

new_candidates = []

for p in whop_profiles:
    pid = p.get("id")
    email = str(p.get("name") or "").strip().lower()
    wname = str(p.get("whop_username") or "").strip().lower()
    notes = str(p.get("notes") or "")
    
    # Must have Email Pass in notes
    if "Email Pass:" not in notes:
        continue
        
    # Check if email is already in dashboard
    if email in existing_emails:
        continue
        
    # Check if whop_username is already in dashboard
    if wname and wname in existing_usernames and wname != "appdevelopment":
        continue
        
    new_candidates.append(p)

print(f"\nTotal TRULY NEW registered candidate browser profiles: {len(new_candidates)}")

if new_candidates:
    selected = new_candidates[0]
    print("\n=== SELECTED 1 BRAND NEW CANDIDATE ===")
    print(f"ID: {selected.get('id')}")
    print(f"Email: {selected.get('name')}")
    print(f"Notes: {selected.get('notes')}")
    print(f"Proxy: {selected.get('proxy_name')} ({selected.get('proxy_server')})")
    print(f"Browser Type: {selected.get('browser_type')}")
