import os
import sys
import time
import requests

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

profile = None
for p in db.list_profiles(platform="whop"):
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

# Download image locally
local_img_path = os.path.abspath(".tmp/dawnmuros_avatar.jpg")
os.makedirs(".tmp", exist_ok=True)

r = requests.get(avatar_url)
with open(local_img_path, "wb") as f:
    f.write(r.content)
print(f"[INFO] Downloaded avatar image to {local_img_path} ({os.path.getsize(local_img_path)} bytes)")

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("[INFO] Navigating to Whop user settings page...")
    page.goto("https://whop.com/settings/profile", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    print("[INFO] Page title:", page.title())
    print("[INFO] Page URL:", page.url)
    
    # Check if logged in or redirected to login
    if "login" in page.url:
        print("[WARNING] Redirected to login page.")
    else:
        print("[SUCCESS] Navigated to profile settings page!")
        
    # Look for file input elements on page
    file_inputs = page.locator("input[type='file']")
    count = file_inputs.count()
    print(f"[INFO] Found {count} file input elements on page.")
    
    if count > 0:
        print("[INFO] Setting avatar file via input[type='file']...")
        file_inputs.first.set_input_files(local_img_path)
        time.sleep(5)
        
        # Look for Save button
        for save_sel in ["button:has-text('Save')", "button:has-text('Save changes')", "button:has-text('Update')"]:
            try:
                save_btn = page.locator(save_sel).first
                if save_btn.count() > 0 and save_btn.is_visible():
                    print(f"[INFO] Clicking save button: {save_sel}")
                    save_btn.click()
                    time.sleep(5)
                    break
            except Exception:
                pass
                
        # Take screenshot of final settings state
        os.makedirs(".tmp/screenshots", exist_ok=True)
        final_shot = ".tmp/screenshots/avatar_update_result.png"
        page.screenshot(path=final_shot)
        print(f"[SUCCESS] Saved final screenshot to {final_shot}")
