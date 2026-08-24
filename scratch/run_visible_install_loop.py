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

print(f"[INFO] Launching VISIBLE browser for @dawnmuros to install app across all communities...")

with BrowserManager(profile, headless=False) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # 1. Load install page
    page.goto(install_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    
    # Total buttons count
    btns = page.locator("button:has-text('Add'), a:has-text('Add')")
    total_count = btns.count()
    print(f"[INFO] Found {total_count} total community options in install list.")
    
    installed_log = []
    
    for i in range(total_count):
        print(f"\n=======================================================")
        print(f"   Processing Community [{i+1}/{total_count}]")
        print(f"=======================================================")
        
        # Navigate to install URL
        page.goto(install_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2.5)
        
        # Refresh locator
        current_btns = page.locator("button:has-text('Add'), a:has-text('Add')")
        if i >= current_btns.count():
            print(f"[INFO] Finished all available items! (Index {i} exceeded count {current_btns.count()})")
            break
            
        target_btn = current_btns.nth(i)
        
        try:
            row_info = target_btn.evaluate("el => el.closest('div').innerText").replace('\n', ' ')
        except Exception:
            row_info = f"Community #{i+1}"
            
        print(f"[ACTION] Clicking 'Add' for [{i+1}/{total_count}]: {row_info[:70]}")
        target_btn.click()
        time.sleep(3.5)
        
        # Check if an Approve / Install / Allow modal button appeared
        modal_btns = page.locator("button:has-text('Approve'), button:has-text('Install'), button:has-text('Allow'), button:has-text('Confirm'), button:has-text('Add app')")
        if modal_btns.count() > 0 and modal_btns.first.is_visible():
            print("[ACTION] Found approval modal button. Clicking Approve/Install...")
            modal_btns.first.click()
            time.sleep(4)
            
        print(f"[STATUS] Result URL for [{i+1}/{total_count}]: {page.url}")
        installed_log.append({
            "num": i+1,
            "community": row_info[:70],
            "url": page.url
        })

print("\n=======================================================")
print(f"🎉 COMPLETED ALL {len(installed_log)} COMMUNITY INSTALLATIONS!")
print("=======================================================")
for item in installed_log:
    print(f"  [{item['num']}] {item['community']} -> {item['url']}")
