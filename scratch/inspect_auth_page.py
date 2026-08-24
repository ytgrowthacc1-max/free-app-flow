import os
import sys
import time
import secrets
import hashlib
import base64
import urllib.parse

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

profile = None
for p in db.list_profiles(platform="whop"):
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

client_id = "app_oPIxXnyEJ8uxNK"
redirect_uri = "http://localhost:8000/callback"
code_verifier = secrets.token_urlsafe(32)
hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')

scopes = "openid profile email company:create company:basic:read company:update company:balance:read experience:create experience:attach experience:detach experience:update forum:read forum:post:create chat:read chat:message:create chat:moderate support_chat:read support_chat:message:create support_chat:create dms:read dms:message:manage dms:channel:manage file:create file:read file:delete user:profile:update product:basic:read product:create product:update checkout_configuration:basic:read checkout_configuration:create courses:read courses:update affiliate:basic:read affiliate:create stats:read"

params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": scopes,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "state": "test",
    "nonce": secrets.token_urlsafe(16)
}
auth_url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto(auth_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    
    print("\n--- PAGE DETAILS ---")
    print("Final URL:", page.url)
    print("Page Title:", page.title())
    
    body_text = page.locator("body").inner_text()
    print("\nPage Body Text Snippet:\n", body_text[:600])
