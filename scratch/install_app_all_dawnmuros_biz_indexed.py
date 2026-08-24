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

results = []

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("[INFO] Loading install page...")
    page.goto(install_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    
    # Get total count of businesses listed
    buttons = page.locator("button:has-text('Add'), a:has-text('Add')")
    total_biz = buttons.count()
    print(f"[INFO] Found {total_biz} business install options on page.")
    
    for idx in range(total_biz):
        print(f"\n--- Installing to Business #{idx + 1} of {total_biz} ---")
        page.goto(install_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        btns = page.locator("button:has-text('Add'), a:has-text('Add')")
        if idx >= btns.count():
            print(f"[WARNING] Index {idx} out of range (count: {btns.count()})")
            break
            
        target_btn = btns.nth(idx)
        try:
            row_text = target_btn.evaluate("el => el.closest('div').innerText").replace('\n', ' ')
        except Exception:
            row_text = f"Business #{idx + 1}"
            
        print(f"[INFO] Clicking 'Add' for [{idx+1}/{total_biz}]: {row_text[:60]}")
        target_btn.click()
        time.sleep(4)
        
        print(f"Result URL: {page.url}")
        results.append({
            "biz_index": idx + 1,
            "row": row_text[:60],
            "final_url": page.url
        })

print("\n=======================================================")
print(f"🎉 COMPLETED APP INSTALLATION FOR ALL {len(results)} BUSINESSES!")
print("=======================================================")
for r in results:
    print(f" [{r['biz_index']}] {r['row']} => {r['final_url']}")
