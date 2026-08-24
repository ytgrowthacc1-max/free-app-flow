import urllib.parse
import sys
import secrets
import hashlib
import base64

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

test_combos = [
    "openid profile email",
    "openid profile email company:create",
    "openid profile email company:create company:basic:read",
    "openid profile email company:create company:basic:read user:profile:update",
    "openid profile email company:create company:basic:read user:profile:update experience:create",
    "openid profile email company:create company:basic:read user:profile:update experience:create forum:read forum:post:create",
    "openid profile email company:create company:basic:read user:profile:update experience:create forum:read forum:post:create chat:read chat:message:create",
    "openid profile email company:create company:basic:read user:profile:update experience:create forum:read forum:post:create chat:read chat:message:create support_chat:read support_chat:message:create dms:read dms:message:manage",
]

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    for combo in test_combos:
        code_verifier = secrets.token_urlsafe(32)
        hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": combo,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": "test",
            "nonce": secrets.token_urlsafe(16)
        }
        url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        curr = page.url
        if "invalid_scope" in curr:
            print(f"[-] FAILED (invalid_scope): {combo}")
        else:
            print(f"[+] PASSED: {combo}")
            print(f"    URL: {curr}")
