import os
import sys
import time
import json
import sqlite3

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

# Find profile for account #54 (@dawnmuros)
profiles = db.list_profiles(platform="whop")
profile = None
for p in profiles:
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

if not profile:
    print("[ERROR] Could not find profile for Account #54")
    sys.exit(1)

print(f"[INFO] Found profile: {profile.get('name')} (Account #{profile.get('account_number')})")

img_path = os.path.abspath(".tmp/profile_pic.jpg")
if not os.path.exists(img_path):
    print(f"[ERROR] Image path does not exist: {img_path}")
    sys.exit(1)

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    print("[INFO] Navigating to Whop Account Settings...")
    page.goto("https://whop.com/settings/account/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)
    
    print("[INFO] Current URL:", page.url)
    
    # Take initial screenshot
    os.makedirs(".tmp/screenshots", exist_ok=True)
    page.screenshot(path=".tmp/screenshots/profile_settings_1.png")
    
    # Try finding file input for profile picture avatar
    file_input = page.locator("input[type='file']").first
    if file_input.count() > 0:
        print("[INFO] Found file input element. Setting file...")
        file_input.set_input_files(img_path)
        time.sleep(3)
        
        # Look for save/submit buttons
        for selector in [
            "button:has-text('Save')",
            "button:has-text('Update')",
            "button:has-text('Save changes')",
            "button[type='submit']"
        ]:
            try:
                btn = page.locator(selector).first
                if btn.count() > 0 and btn.is_visible():
                    print(f"[INFO] Clicking button: {selector}")
                    btn.click()
                    time.sleep(3)
                    break
            except Exception as err:
                pass
                
        page.screenshot(path=".tmp/screenshots/profile_settings_updated.png")
        print("[SUCCESS] Uploaded profile picture and saved!")
    else:
        print("[WARNING] Could not find input[type='file']. Checking for edit avatar button...")
        # Check for avatar edit overlay / click trigger
        avatar_btn = page.locator("button:has(img), div:has(img):has-text('Edit'), label:has-text('Upload')").first
        if avatar_btn.count() > 0:
            print("[INFO] Clicking avatar upload trigger...")
            avatar_btn.click()
            time.sleep(2)
            file_input = page.locator("input[type='file']").first
            if file_input.count() > 0:
                file_input.set_input_files(img_path)
                time.sleep(3)
                page.screenshot(path=".tmp/screenshots/profile_settings_updated.png")
                print("[SUCCESS] Uploaded profile picture via trigger!")
            else:
                print("[ERROR] Still no file input found after trigger click.")
        else:
            print("[ERROR] No avatar trigger button found on settings page.")
