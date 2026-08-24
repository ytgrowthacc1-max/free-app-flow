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
    # Find profile 50
    profiles = db.list_profiles(platform="whop")
    profile = None
    for p in profiles:
        if p.get("account_number") == 50:
            profile = p
            break
            
    if not profile:
        print("Profile for Account #50 not found.")
        return
        
    print(f"Launching browser for {profile.get('name')} (Account #50) with geoip=False...")
    proxy = build_proxy(profile)
    user_data_dir = profile.get("user_data_dir")
    fp_dict = profile.get("fingerprint")
    fingerprint = try_restore_fingerprint(fp_dict) if fp_dict else None
    
    kwargs = {
        "headless": True,
        "geoip": False,  # Prevent geoip check hang
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
        
        print("Navigating to https://whop.com/...")
        page.goto("https://whop.com/", wait_until="networkidle", timeout=60000)
        
        # Take screenshot to see who is logged in
        os.makedirs(".tmp/screenshots", exist_ok=True)
        shot_path = ".tmp/screenshots/brian_profile_check.png"
        page.screenshot(path=shot_path)
        print(f"Screenshot saved to {shot_path}")
        
        # Print page url and title
        print("Current URL:", page.url)
        print("Page Title:", page.title())

if __name__ == "__main__":
    main()
