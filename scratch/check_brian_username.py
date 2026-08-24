import sys
import os
import time

# Patch yaml CLoader before importing anything that might use it
import yaml
if not hasattr(yaml, 'CLoader'):
    yaml.CLoader = yaml.Loader
    yaml.CDumper = yaml.Dumper

# Add paths to sys.path
sys.path.append(r"c:\Python\Browsing Skill Agent\execution")
sys.path.append(r"c:\Python\Browsing Skill Agent")

from camoufox.sync_api import Camoufox
from _profile_browser_worker import build_proxy, try_restore_fingerprint
import profile_db as db

def main():
    profiles = db.list_profiles(platform="whop")
    profile = None
    for p in profiles:
        if p.get("account_number") == 50:
            profile = p
            break
            
    if not profile:
        print("Profile for Account #50 not found.")
        return
        
    proxy = build_proxy(profile)
    user_data_dir = profile.get("user_data_dir")
    fp_dict = profile.get("fingerprint")
    fingerprint = try_restore_fingerprint(fp_dict) if fp_dict else None
    
    kwargs = {
        "headless": True,
        "geoip": False,
        "persistent_context": True,
        "locale": "en-US",
        "i_know_what_im_doing": True
    }
    if proxy:
        kwargs["proxy"] = proxy
    if user_data_dir:
        kwargs["user_data_dir"] = os.path.abspath(user_data_dir)
    if fingerprint:
        kwargs["fingerprint"] = fingerprint
        
    with Camoufox(**kwargs) as browser:
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({'width': 1280, 'height': 800})
        
        print("Navigating to https://whop.com/settings...")
        page.goto("https://whop.com/settings", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        
        # Take screenshot of settings page
        os.makedirs(".tmp/screenshots", exist_ok=True)
        shot_path = ".tmp/screenshots/brian_settings_check.png"
        page.screenshot(path=shot_path)
        print(f"Screenshot saved to {shot_path}")
        
        print("Current URL:", page.url)
        
        # Print body text to see if we can find username
        body_text = page.locator("body").inner_text()
        print("Does 'briandelgadillo' appear in page text?", "briandelgadillo" in body_text.lower())
        print("Does 'appdevelopment' appear in page text?", "appdevelopment" in body_text.lower())
        
        # Try to find user profile input or headings
        for selector in ["h1", "h2", "input[value]", "span"]:
            try:
                elements = page.locator(selector).all()
                for el in elements:
                    text = el.inner_text() or el.get_attribute("value") or ""
                    if "briandelgadillo" in text.lower() or "appdevelopment" in text.lower():
                        print(f"Found match [{selector}]: {text}")
            except Exception:
                pass

if __name__ == "__main__":
    main()
