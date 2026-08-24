import urllib.parse
import sys

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

# Standard Whop OAuth scopes
scope_str = "openid profile email company:create company:basic:read experience:create forum:read forum:post:create chat:read chat:message:create support_chat:read support_chat:message:create dms:read dms:message:manage user:profile:update"

auth_url = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={urllib.parse.quote(scope_str)}"

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto(auth_url, wait_until="domcontentloaded", timeout=15000)
    print("Page URL:", page.url)
    if "invalid_scope" in page.url:
        print("[ERROR] Scope combo is INVALID!")
    else:
        print("[SUCCESS] Scope combo is VALID!")
