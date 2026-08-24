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

if not profile:
    print("[ERROR] Could not find profile 54")
    sys.exit(1)

app_url = "https://whop.com/apps/app_tHhlowWfWKDkIF/"

print(f"[INFO] Launching browser for @dawnmuros to install app {app_url}...")
with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("[INFO] Navigating to app store page...")
    page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    
    print("Page URL:", page.url)
    print("Page Title:", page.title())
    
    os.makedirs(".tmp/screenshots", exist_ok=True)
    page.screenshot(path=".tmp/screenshots/app_store_page.png")
    
    # Check for Install or Add to Whop button
    buttons = page.locator("button, a").all_inner_texts()
    install_btns = [b for b in buttons if any(k in b.lower() for k in ["install", "add", "get", "use"])]
    print("Found potential install buttons:", install_btns)
    
    # Try clicking Install / Add button
    for text in ["Add app", "Install", "Add to Whop", "Get App", "Install App"]:
        btn = page.locator(f"button:has-text('{text}'), a:has-text('{text}')").first
        if btn.count() > 0 and btn.is_visible():
            print(f"[INFO] Clicking button: {text}")
            btn.click()
            time.sleep(5)
            page.screenshot(path=".tmp/screenshots/after_install_click.png")
            print("Current URL after click:", page.url)
            break
