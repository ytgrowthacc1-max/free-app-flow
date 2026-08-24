import os
import sys
import time
import subprocess
import glob
import json

# Kill lingering processes and remove lock files
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

# File-backed persistent state
state_file = r"C:\Python\WHOP AUTOMATION AGENTIC\.tmp\installed_app_tHhlowWfWKDkIF_companies.json"
os.makedirs(os.path.dirname(state_file), exist_ok=True)

installed_companies = set()
if os.path.exists(state_file):
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            installed_companies = set(data.get("installed", []))
            print(f"[STATE] Loaded {len(installed_companies)} previously installed communities from persistent file.")
    except Exception as e:
        print(f"[STATE WARNING] Could not load state file: {e}")

def save_installed_state():
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump({"installed": list(installed_companies)}, f, indent=2)

print(f"[INFO] Launching 2-Step Persistent Visible Browser Installation for @dawnmuros...")

with BrowserManager(profile, headless=False) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    def load_install_page():
        for attempt in range(3):
            try:
                page.goto(install_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(3)
                return True
            except Exception as e:
                print(f"[RETRY] Navigation issue (attempt {attempt+1}): {e}")
                time.sleep(2)
        return False

    load_install_page()
    
    max_loops = 30
    for loop in range(max_loops):
        print(f"\n=======================================================")
        print(f"               Scan Loop #{loop + 1}")
        print(f"=======================================================")
        
        load_install_page()
        
        add_btns = page.locator("button:has-text('Add'), a:has-text('Add')").all()
        print(f"[INFO] Found {len(add_btns)} total 'Add' buttons on install page.")
        
        if not add_btns:
            print("[INFO] No 'Add' buttons found on page. Finished!")
            break
            
        target_btn = None
        target_name = None
        
        for btn in add_btns:
            try:
                row_txt = btn.evaluate("el => el.closest('div').innerText").strip().replace('\n', ' ')
                comp_name = row_txt.split("Add")[0].strip() or row_txt[:40]
            except Exception:
                comp_name = "Unknown Company"
                
            if comp_name not in installed_companies:
                target_btn = btn
                target_name = comp_name
                break
                
        if not target_btn:
            print(f"[INFO] All {len(installed_companies)} discovered communities have been processed and saved!")
            break
            
        print(f"\n[STEP 1] Pressing 'Add' for company: '{target_name}'")
        target_btn.click()
        time.sleep(4)
        
        print("[STEP 2] Checking for 'Approve' / 'Install' / 'Authorize' button...")
        approved = False
        for btn_text in ["Approve", "Install", "Allow", "Authorize", "Add app", "Confirm"]:
            approve_btn = page.locator(f"button:has-text('{btn_text}'), a:has-text('{btn_text}')").first
            if approve_btn.count() > 0 and approve_btn.is_visible():
                print(f"[ACTION] Found modal button '{btn_text}'. Pressing Approve...")
                approve_btn.click()
                time.sleep(5)
                approved = True
                break
                
        if not approved:
            print(f"[INFO] No separate modal button required or auto-approved. Current URL: {page.url}")
            
        installed_companies.add(target_name)
        save_installed_state()
        print(f"[SUCCESS] Installed app into '{target_name}' and saved to disk! (Total installed: {len(installed_companies)})")

print("\n=======================================================")
print(f"🎉 FINISHED 2-STEP APP INSTALLATION FOR ALL {len(installed_companies)} COMMUNITIES!")
print("=======================================================")
for c in installed_companies:
    print(f" - {c}")
