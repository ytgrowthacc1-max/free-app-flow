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
        
        print("Navigating to https://whop.com/...")
        page.goto("https://whop.com/", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        
        # Execute JS to fetch session info or find next data
        session_info = page.evaluate("""() => {
            try {
                // Try fetching NEXT_DATA or state
                const nextDataEl = document.getElementById('__NEXT_DATA__');
                if (nextDataEl) {
                    const data = JSON.parse(nextDataEl.textContent);
                    return { source: '__NEXT_DATA__', props: data.props };
                }
            } catch (e) {
                return { error: e.toString() };
            }
            return { not_found: true };
        }""")
        
        print("NEXT DATA check:")
        import json
        # Search for username or id in the NEXT DATA
        session_str = json.dumps(session_info)
        print("Length of session info:", len(session_str))
        
        if "briandelgadillo" in session_str.lower():
            print("Found 'briandelgadillo' in NEXT DATA!")
        if "appdevelopment" in session_str.lower():
            print("Found 'appdevelopment' in NEXT DATA!")
            
        # Write first 2000 chars of NEXT DATA to see structure
        print("Snippet:", session_str[:1000])

if __name__ == "__main__":
    main()
