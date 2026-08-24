import os
import sys
import time
import subprocess
import glob
import json
import requests

# Kill lingering browser processes
subprocess.run("taskkill /f /im camoufox.exe /im firefox.exe /im chrome.exe", shell=True, capture_output=True)
time.sleep(2)

lock_files = glob.glob(r"C:\Python\Browsing Skill Agent\.profiles\**\parent.lock", recursive=True)
for lock in lock_files:
    try:
        os.remove(lock)
    except Exception:
        pass

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    prof_data = json.load(f)

token = prof_data.get("oauth_token")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

target_app_id = "app_tHhlowWfWKDkIF"

def get_company_app_status():
    comp_res = requests.get("https://api.whop.com/v1/companies", headers=headers)
    companies = comp_res.json().get("data", []) if comp_res.status_code == 200 else []
    
    installed = []
    uninstalled = []
    
    for c in companies:
        c_id = c.get("id")
        c_title = c.get("title")
        exp_res = requests.get(f"https://api.whop.com/v1/experiences?company_id={c_id}", headers=headers)
        
        has_app = False
        if exp_res.status_code == 200:
            exps = exp_res.json().get("data", [])
            for exp in exps:
                if exp.get("app", {}).get("id") == target_app_id:
                    has_app = True
                    break
        
        if has_app:
            installed.append(c)
        else:
            uninstalled.append(c)
            
    return installed, uninstalled

print("--- Checking live Whop API state before browser launch ---")
installed_before, uninstalled_before = get_company_app_status()
print(f"[API CHECK] Already Installed: {len(installed_before)} | Remaining to Install: {len(uninstalled_before)}")

if not uninstalled_before:
    print("[SUCCESS] All companies already have the app installed! Nothing to do.")
    sys.exit(0)

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

profile = None
for p in db.list_profiles(platform="whop"):
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

install_url = f"https://whop.com/apps/{target_app_id}/install/"

print(f"\n[INFO] Launching VISIBLE browser for @dawnmuros to install {len(uninstalled_before)} remaining companies...")

with BrowserManager(profile, headless=False) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    for idx, comp in enumerate(uninstalled_before):
        comp_id = comp.get("id")
        comp_title = comp.get("title")
        
        print(f"\n=======================================================")
        print(f" [{idx+1}/{len(uninstalled_before)}] Installing to: '{comp_title}' ({comp_id})")
        print(f"=======================================================")
        
        page.goto(install_url, wait_until="domcontentloaded", timeout=45000)
        time.sleep(3)
        
        # Locate company card matching comp_title or comp_id
        add_btns = page.locator("button:has-text('Add'), a:has-text('Add')").all()
        target_btn = None
        
        for btn in add_btns:
            try:
                row_txt = btn.evaluate("el => el.closest('div').innerText").strip().replace('\n', ' ')
                if comp_title.lower() in row_txt.lower():
                    target_btn = btn
                    break
            except Exception:
                pass
                
        if not target_btn and add_btns:
            print(f"[WARNING] Exact name match for '{comp_title}' not found in DOM row text. Using next available button.")
            target_btn = add_btns[0]
            
        if not target_btn:
            print(f"[ERROR] No Add button found on page for '{comp_title}'. Skipping.")
            continue
            
        print(f"[STEP 1] Clicking 'Add' for '{comp_title}'...")
        target_btn.click()
        time.sleep(4)
        
        print(f"[STEP 2] Checking for 'Approve' / 'Install' / 'Authorize' modal button...")
        approved = False
        for btn_text in ["Approve", "Install", "Allow", "Authorize", "Add app", "Confirm"]:
            approve_btn = page.locator(f"button:has-text('{btn_text}'), a:has-text('{btn_text}')").first
            if approve_btn.count() > 0 and approve_btn.is_visible():
                print(f"[ACTION] Found modal button '{btn_text}'. Pressing Approve...")
                approve_btn.click()
                time.sleep(5)
                approved = True
                break
                
        # Re-verify via Whop API that experience is now installed!
        exp_check = requests.get(f"https://api.whop.com/v1/experiences?company_id={comp_id}", headers=headers)
        installed_now = False
        if exp_check.status_code == 200:
            for exp in exp_check.json().get("data", []):
                if exp.get("app", {}).get("id") == target_app_id:
                    installed_now = True
                    break
                    
        if installed_now:
            print(f" [API VERIFIED] Successfully installed app into '{comp_title}'!")
        else:
            print(f" [API PENDING] App installation submitted for '{comp_title}'.")

print("\n--- Finalizing Audit ---")
installed_after, uninstalled_after = get_company_app_status()
print(f"\n=======================================================")
print(f"🎉 FINAL RESULT: Installed: {len(installed_after)} / {len(installed_after) + len(uninstalled_after)}")
print("=======================================================")
