import os
import sys
import time

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager
import urllib.parse
import secrets
import hashlib
import base64
import requests

WHOP_AUTOMATION_DIR = r"C:\Python\WHOP AUTOMATION AGENTIC"
sys.path.insert(0, WHOP_AUTOMATION_DIR)
from execution.app_config import get_whop_app_credentials
from execution.whop_auth import update_profile_token_only

client_id, client_secret, redirect_uri = get_whop_app_credentials()
redirect_uri = "http://localhost:8000/callback"

profiles = db.list_profiles(platform="whop")
profile = None
for p in profiles:
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

code_verifier = secrets.token_urlsafe(32)
hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')
oauth_state = secrets.token_urlsafe(16)

scopes = "ad_campaign:create ad_campaign:update affiliate:basic:read affiliate:create affiliate:update ai_prompt:create stats:read experience:attach experience:create experience:delete experience:detach experience:hidden_experience:read experience:update company:log:read chat:moderate chat:message:create chat:read dms:read dms:message:manage dms:channel:manage custom_emoji:update checkout_configuration:basic:read checkout_configuration:create checkout_configuration:delete company:balance:read company:manage_checkout company:basic:read company:create company:update social_link:update courses:read courses:update course_lesson_interaction:read course_analytics:read developer:basic:read developer:create_app developer:manage_builds developer:update_app forum:post:create forum:read membership:basic:read membership:cancel membership:manage membership:terminate payment:basic:read payout:create payout:delete file:create file:delete file:read product:basic:read product:create product:delete product:update push_notification:send promo_code:create promo_code:delete promo_code:update user:profile:update support_chat:create support_chat:read support_chat:message:create"

params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": scopes,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "state": oauth_state
}
auth_url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)

print("[INFO] OAuth URL:", auth_url)

captured_code = None

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    def on_nav(url):
        global captured_code
        if "code=" in url:
            parsed = urllib.parse.urlparse(url)
            code_list = urllib.parse.parse_qs(parsed.query).get("code")
            if code_list:
                captured_code = code_list[0]
                print("[SUCCESS] Captured auth code:", captured_code)

    page.on("framenavigated", lambda f: on_nav(f.url))
    page.on("request", lambda r: on_nav(r.url))
    
    print("[INFO] Navigating to authorization URL...")
    try:
        page.goto(auth_url, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print("[WARNING] Navigation issue:", e)
        
    time.sleep(3)
    
    start_t = time.time()
    while time.time() - start_t < 40:
        if captured_code:
            break
        # Click Allow / Approve / Authorize if present
        for sel in [
            "button:has-text('Allow')",
            "button:has-text('Approve')",
            "button:has-text('Authorize')",
            "button:has-text('Allow Access')",
            "//button[contains(., 'Allow')]",
            "//button[contains(., 'Approve')]"
        ]:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    print("[INFO] Clicking approval button:", sel)
                    btn.click()
                    time.sleep(2)
                    break
            except Exception:
                pass
        time.sleep(1)

if not captured_code:
    print("[ERROR] Failed to capture authorization code.")
    sys.exit(1)

# Exchange token
token_url = "https://api.whop.com/oauth/token"
payload = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": captured_code,
    "code_verifier": code_verifier,
    "redirect_uri": redirect_uri
}

r = requests.post(token_url, json=payload)
print("Token status:", r.status_code)
if r.status_code == 200:
    t_data = r.json()
    acc_token = t_data.get("access_token")
    ref_token = t_data.get("refresh_token")
    bot_id = "user_lO14mFc5tBKN3"
    update_profile_token_only(bot_id, acc_token, ref_token)
    print(f"[SUCCESS] Authorized bot {bot_id} with ALL 60 scopes!")
else:
    print("Token Exchange Failed:", r.text)
