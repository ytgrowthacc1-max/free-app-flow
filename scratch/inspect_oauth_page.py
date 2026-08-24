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

auth_url = "https://api.whop.com/oauth/authorize?client_id=app_oPIxXnyEJ8uxNK&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback&response_type=code&scope=ad_campaign%3Acreate+ad_campaign%3Aupdate+affiliate%3Abasic%3Aread+affiliate%3Acreate+affiliate%3Aupdate+ai_prompt%3Acreate+stats%3Aread+experience%3Aattach+experience%3Acreate+experience%3Adelete+experience%3Adetach+experience%3Ahidden_experience%3Aread+experience%3Aupdate+company%3Alog%3Aread+chat%3Amoderate+chat%3Amessage%3Acreate+chat%3Aread+dms%3Aread+dms%3Amessage%3Amanage+dms%3Achannel%3Amanage+custom_emoji%3Aupdate+checkout_configuration%3Abasic%3Aread+checkout_configuration%3Acreate+checkout_configuration%3Adelete+company%3Abalance%3Aread+company%3Amanage_checkout+company%3Abasic%3Aread+company%3Acreate+company%3Aupdate+social_link%3Aupdate+courses%3Aread+courses%3Aupdate+course_lesson_interaction%3Aread+course_analytics%3Aread+developer%3Abasic%3Aread+developer%3Acreate_app+developer%3Amanage_builds+developer%3Aupdate_app+forum%3Apost%3Acreate+forum%3Aread+membership%3Abasic%3Aread+membership%3Acancel+membership%3Amanage+membership%3Aterminate+payment%3Abasic%3Aread+payout%3Acreate+payout%3Adelete+file%3Acreate+file%3Adelete+file%3Aread+product%3Abasic%3Aread+product%3Acreate+product%3Adelete+product%3Aupdate+push_notification%3Asend+promo_code%3Acreate+promo_code%3Adelete+promo_code%3Aupdate+user%3Aprofile%3Aupdate+support_chat%3Acreate+support_chat%3Aread+support_chat%3Amessage%3Acreate&code_challenge=eqkemzCHq-5kkbzUJ7dTM5FoIYosgam-hV8KUpnsdaM&code_challenge_method=S256&state=test"

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto(auth_url, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    
    os.makedirs(".tmp/screenshots", exist_ok=True)
    page.screenshot(path=".tmp/screenshots/oauth_page.png")
    
    print("Page URL:", page.url)
    print("Page Title:", page.title())
    
    buttons = page.eval_on_selector_all(
        "button, a, input[type='submit']",
        "els => els.map(e => ({text: e.innerText || e.value || '', class: e.className, tag: e.tagName}))"
    )
    print("\nButtons & Clickables:")
    for b in buttons:
        print(b)
