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

test_list = [
    "openid", "profile", "email",
    "company:create", "company:basic:read", "company:update", "company:balance:read",
    "experience:create", "experience:attach", "experience:detach", "experience:update",
    "forum:read", "forum:post:create",
    "chat:read", "chat:message:create", "chat:moderate",
    "support_chat:read", "support_chat:message:create", "support_chat:create",
    "dms:read", "dms:message:manage", "dms:channel:manage",
    "file:create", "file:read", "file:delete",
    "user:profile:update",
    "product:basic:read", "product:create", "product:update",
    "checkout_configuration:basic:read", "checkout_configuration:create",
    "courses:read", "courses:update",
    "affiliate:basic:read", "affiliate:create",
    "stats:read"
]

valid_scopes = []
invalid_scopes = []

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    for s in test_list:
        code_verifier = secrets.token_urlsafe(32)
        hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": s,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": "test"
        }
        url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        curr = page.url
        if "invalid_scope" in curr:
            print(f"[-] INVALID: {s}")
            invalid_scopes.append(s)
        else:
            print(f"[+] VALID:   {s}")
            valid_scopes.append(s)

print("\n================ RESULT ================")
print(f"Valid ({len(valid_scopes)}):", valid_scopes)
print(f"Invalid ({len(invalid_scopes)}):", invalid_scopes)

# Test combined valid scopes
valid_str = " ".join(valid_scopes)
code_verifier = secrets.token_urlsafe(32)
hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')

params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": valid_str,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "state": "test"
}
combo_url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
page.goto(combo_url, wait_until="domcontentloaded", timeout=15000)
print("\nCombined Test URL:", page.url)
if "invalid_scope" not in page.url:
    print("[SUCCESS] COMBINED SCOPE TEST PASSED FOR @dawnmuros!")
    print("FINAL WORKING SCOPE STRING:")
    print(f'"{valid_str}"')
