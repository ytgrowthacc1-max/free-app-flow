import os
import sys
import time
import json

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

profile = None
for p in db.list_profiles(platform="whop"):
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

install_url = "https://whop.com/apps/app_tHhlowWfWKDkIF/install/"

installed_companies = []

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("[INFO] Launching installation loop for all @dawnmuros businesses...")
    
    # We will loop until all 'Add' buttons are processed
    max_installs = 25
    for attempt in range(max_installs):
        print(f"\n--- Iteration {attempt + 1} ---")
        page.goto(install_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(4)
        
        # Get count of remaining 'Add' buttons
        add_buttons = page.locator("button:has-text('Add'), a:has-text('Add')").all()
        print(f"Found {len(add_buttons)} businesses remaining for installation.")
        
        if not add_buttons:
            print("[INFO] No more uninstalled businesses found!")
            break
            
        # Click the first remaining 'Add' button
        btn = add_buttons[0]
        # Get row parent text to log company name
        try:
            row_text = btn.evaluate("el => el.closest('div').innerText").replace('\n', ' ')
        except Exception:
            row_text = f"Business #{attempt + 1}"
            
        print(f"[INFO] Clicking 'Add' for: {row_text[:60]}")
        btn.click()
        time.sleep(5)
        
        print("Redirected to URL:", page.url)
        installed_companies.append({
            "index": attempt + 1,
            "row": row_text[:60],
            "url": page.url
        })
        time.sleep(1)

print("\n=======================================================")
print(f"🎉 INSTALLED APP TO {len(installed_companies)} BUSINESSES FOR @dawnmuros!")
print("=======================================================")
for item in installed_companies:
    print(f" - [{item['index']}] {item['row']} => {item['url']}")
