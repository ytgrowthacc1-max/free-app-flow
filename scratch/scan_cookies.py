import os
import json
import sqlite3
import glob

base_profiles = r"C:\Python\Browsing Skill Agent\.profiles"

profiles_with_whop_cookies = []

for item in os.listdir(base_profiles):
    pdir = os.path.join(base_profiles, item)
    if not os.path.isdir(pdir):
        continue
    
    # Check all cookies files
    sqlite_files = glob.glob(os.path.join(pdir, "**", "Cookies"), recursive=True) + glob.glob(os.path.join(pdir, "cookies.sqlite"), recursive=True)
    
    has_whop = False
    for cf in sqlite_files:
        if os.path.isfile(cf):
            try:
                conn = sqlite3.connect(cf)
                cur = conn.cursor()
                # Query cookies table or moz_cookies table
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                if "cookies" in tables:
                    cur.execute("SELECT count(*) FROM cookies WHERE host_key LIKE '%whop.com%'")
                    c = cur.fetchone()[0]
                    if c > 0:
                        has_whop = True
                elif "moz_cookies" in tables:
                    cur.execute("SELECT count(*) FROM moz_cookies WHERE host LIKE '%whop.com%'")
                    c = cur.fetchone()[0]
                    if c > 0:
                        has_whop = True
                conn.close()
            except Exception:
                pass
        if has_whop:
            break
            
    if has_whop:
        profiles_with_whop_cookies.append(item)

print(f"Total profiles with Whop cookies in .profiles: {len(profiles_with_whop_cookies)}")
for pid in profiles_with_whop_cookies:
    print(" - Profile Dir:", pid)
