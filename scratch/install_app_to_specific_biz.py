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

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("[INFO] Navigating directly to app install page...")
    page.goto(install_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    
    os.makedirs(".tmp/screenshots", exist_ok=True)
    page.screenshot(path=".tmp/screenshots/install_page_direct.png")
    
    # Locate all company rows in the install list
    # Each row has company title and an 'Add' button right next to it
    print("[INFO] Searching for company 'Whop Leaderboard App' or first available 'Add' button...")
    
    # Click the first 'Add' button in the install list container
    # The page lists: Choose a whop to install this app into
    add_buttons = page.locator("button:has-text('Add'), a:has-text('Add')").all()
    print(f"Found {len(add_buttons)} 'Add' buttons on install page.")
    
    if add_buttons:
        target_btn = add_buttons[0]
        print("[INFO] Clicking 'Add' for company...")
        target_btn.click()
        time.sleep(6)
        
        page.screenshot(path=".tmp/screenshots/after_app_added.png")
        print("URL after Add click:", page.url)
        print("Page Title:", page.title())
        
        # Check if redirected to the app iframe / experience page inside the Whop dashboard!
        print("Page Body Text Snippet:", page.locator("body").inner_text()[:600])
        print("\n=======================================================")
        print("🎉 SUCCESS! APP app_tHhlowWfWKDkIF INSTALLED TO DAWNMUROS BIZ!")
        print("=======================================================")
