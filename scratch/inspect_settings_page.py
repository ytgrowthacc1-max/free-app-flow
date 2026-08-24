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
    page.goto("https://whop.com/settings/account/", wait_until="networkidle", timeout=60000)
    time.sleep(3)
    
    # Save full HTML snippet
    html = page.content()
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/settings_page.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Page Title:", page.title())
    print("Page URL:", page.url)
    
    # Find all inputs, buttons, and links
    elements = page.eval_on_selector_all(
        "input, button, a, label",
        "els => els.map(e => ({tag: e.tagName, type: e.type || '', text: e.innerText || '', aria: e.getAttribute('aria-label') || '', class: e.className}))"
    )
    print("\nFound Elements:")
    for el in elements[:40]:
        print(el)
