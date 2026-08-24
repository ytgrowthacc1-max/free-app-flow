import os
import sys
import time
import subprocess
import glob

print("[INFO] Cleaning lingering processes and lock files...")
subprocess.run("taskkill /f /im camoufox.exe /im firefox.exe /im chrome.exe", shell=True, capture_output=True)
time.sleep(2)

lock_files = glob.glob(r"C:\Python\Browsing Skill Agent\.profiles\**\parent.lock", recursive=True)
for lock in lock_files:
    try:
        os.remove(lock)
    except Exception:
        pass

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
    
    # Helper to safely navigate to install URL
    def go_to_install_page():
        for retry in range(3):
            try:
                page.goto(install_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(3)
                return
            except Exception as e:
                print(f"[RETRY] Navigation warning (attempt {retry+1}): {e}")
                time.sleep(2)

    go_to_install_page()
    
    btns = page.locator("button:has-text('Add'), a:has-text('Add')")
    total_count = btns.count()
    print(f"[INFO] Found {total_count} total community options in install list.")
    
    installed_log = []
    
    for i in range(total_count):
        print(f"\n=======================================================")
        print(f"   Processing Community [{i+1}/{total_count}]")
        print(f"=======================================================")
        
        go_to_install_page()
        
        current_btns = page.locator("button:has-text('Add'), a:has-text('Add')")
        if i >= current_btns.count():
            print(f"[INFO] Index {i} exceeds current count {current_btns.count()}, finishing loop.")
            break
            
        target_btn = current_btns.nth(i)
        
        try:
            row_info = target_btn.evaluate("el => el.closest('div').innerText").replace('\n', ' ')
        except Exception:
            row_info = f"Community #{i+1}"
            
        print(f"[ACTION] Clicking 'Add' for [{i+1}/{total_count}]: {row_info[:70]}")
        target_btn.click()
        time.sleep(4)
        
        # Check if an Approve / Install / Allow / Add app modal button appeared
        for btn_text in ["Approve", "Install", "Allow", "Confirm", "Add app"]:
            mbtn = page.locator(f"button:has-text('{btn_text}')").first
            if mbtn.count() > 0 and mbtn.is_visible():
                print(f"[ACTION] Found modal button '{btn_text}'. Clicking...")
                mbtn.click()
                time.sleep(4)
                break
            
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
