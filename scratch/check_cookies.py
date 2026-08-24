import sys
import os
import json
import sqlite3

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db

whop_profiles = db.list_profiles(platform="whop")
base_bots_dir = r"c:\Python\WHOP AUTOMATION AGENTIC\profiles\bots"

existing_emails = set()

if os.path.exists(base_bots_dir):
    for bfolder in os.listdir(base_bots_dir):
        pfile = os.path.join(base_bots_dir, bfolder, "profile.json")
        if os.path.exists(pfile):
            try:
                with open(pfile, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("email"):
                        existing_emails.add(data["email"].lower())
            except Exception:
                pass

print(f"Total existing emails in dashboard: {len(existing_emails)}")

unadded_active_profiles = []

for p in whop_profiles:
    email = str(p.get("name") or "").strip().lower()
    if email in existing_emails:
        continue

    user_dir = p.get("user_data_dir")
    if not user_dir or not os.path.exists(user_dir):
        continue
        
    cookies_db = os.path.join(user_dir, "cookies.sqlite")
    if os.path.exists(cookies_db):
        try:
            conn = sqlite3.connect(cookies_db)
            cur = conn.cursor()
            cur.execute("SELECT name, value, host FROM moz_cookies WHERE host LIKE '%whop%'")
            rows = cur.fetchall()
            conn.close()
            
            cnames = [r[0] for r in rows]
            has_auth = any("_adora_user_id" in c or "session-token" in c or "whop-has-multiple" in c for c in cnames)
            
            if has_auth or len(rows) >= 15:
                unadded_active_profiles.append((p, cnames, len(rows)))
        except Exception as e:
            pass

print(f"Total UN-ADDED active profiles with session cookies: {len(unadded_active_profiles)}\n")

for i, (p, cnames, ccount) in enumerate(unadded_active_profiles, 1):
    pid = p.get("id")
    email = p.get("name")
    notes = p.get("notes")
    print(f"{i}. ID: {pid} | Email: {email}")
    print(f"   Cookies: {ccount} | Notes: {notes}")
    print("---")
