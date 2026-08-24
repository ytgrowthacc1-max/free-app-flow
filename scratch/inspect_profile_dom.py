import os
import sys
import time

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

profile = None
for p in db.list_profiles(platform="whop"):
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://whop.com/settings/profile/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # Save page screenshot
    os.makedirs(".tmp/screenshots", exist_ok=True)
    shot_path = ".tmp/screenshots/whop_profile_settings.png"
    page.screenshot(path=shot_path)
    print(f"[INFO] Saved screenshot to {shot_path}")
    
    # Inspect clickable image / avatar elements
    images = page.eval_on_selector_all(
        "img, svg, button, div[role='button']",
        "els => els.map(e => ({tag: e.tagName, text: e.innerText || '', class: e.className, src: e.src || ''})).filter(x => x.text.includes('Edit') or x.text.includes('Avatar') or x.text.includes('Photo') or x.src.includes('avatar') or x.src.includes('profile'))"
    )
    print("\nPotential Avatar Elements:")
    for img in images:
        print(" ->", img)
