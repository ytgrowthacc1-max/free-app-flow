import sys
import os
import json

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
                        # clean username
                        clean_u = ''.join([c for c in data["bot_username"] if not c.isdigit()]).lower()
                        if clean_u:
                            existing_usernames.add(clean_u)
                    if data.get("email"):
                        existing_emails.add(data["email"].lower())
            except Exception:
                pass

print(f"Total Existing Bots in Dashboard: {len(os.listdir(base_bots_dir))}")

whop_profiles = db.list_profiles(platform="whop")

new_candidates = []

for p in whop_profiles:
    pid = p.get("id")
    email = str(p.get("name") or "").strip().lower()
    wname = str(p.get("whop_username") or "").strip().lower()
    notes = str(p.get("notes") or "")
    
    if "Email Pass:" not in notes:
        continue
        
    if email in existing_emails:
        continue
        
    email_prefix = email.split("@")[0]
    email_clean = ''.join([c for c in email_prefix if not c.isdigit()]).lower()
    
    is_existing = False
    for u in existing_usernames:
        if u and (u in email_clean or email_clean in u):
            is_existing = True
            break
            
    if not is_existing:
        new_candidates.append(p)

print(f"Total TRULY NEW candidate browser profiles available: {len(new_candidates)}\n")

selected_5 = new_candidates[:5]
print("=== SELECTED 5 BRAND NEW CANDIDATES ===")
for i, p in enumerate(selected_5, 1):
    pid = p.get("id")
    email = p.get("name")
    notes = p.get("notes")
    print(f"{i}. ID: {pid}")
    print(f"   Email: {email}")
    print(f"   Notes: {notes}")
    print("---")

print("JSON IDs ARRAY:", [p.get("id") for p in selected_5])
