import urllib.parse
import sys
import os

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

all_scopes = [
    "ad_campaign:create","ad_campaign:update","affiliate:basic:read","affiliate:create","affiliate:update","ai_prompt:create","stats:read","experience:attach","experience:create","experience:delete","experience:detach","experience:hidden_experience:read","experience:update","company:log:read","chat:moderate","chat:message:create","chat:read","dms:read","dms:message:manage","dms:channel:manage","custom_emoji:update","checkout_configuration:basic:read","checkout_configuration:create","checkout_configuration:delete","company:balance:read","company:manage_checkout","company:basic:read","company:update","social_link:update","courses:read","courses:update","course_lesson_interaction:read","course_analytics:read","developer:basic:read","developer:create_app","developer:manage_builds","developer:update_app","forum:post:create","forum:read","membership:basic:read","membership:cancel","membership:manage","membership:terminate","payment:basic:read","payout:create","payout:delete","file:create","file:delete","file:read","product:basic:read","product:create","product:delete","product:update","push_notification:send","promo_code:create","promo_code:delete","promo_code:update","user:profile:update","support_chat:create","support_chat:read","support_chat:message:create","company:create"
]

print(f"Testing {len(all_scopes)} individual scopes with active Camoufox session...")

valid_scopes = []
invalid_scopes = []

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    for scope in all_scopes:
        auth_url = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={scope}"
        page.goto(auth_url, wait_until="domcontentloaded", timeout=15000)
        curr_url = page.url
        if "invalid_scope" in curr_url or "error=" in curr_url:
            print(f"[-] INVALID: {scope}")
            invalid_scopes.append(scope)
        else:
            print(f"[+] VALID:   {scope}")
            valid_scopes.append(scope)

print("\n================ RESULT ================")
print(f"Valid ({len(valid_scopes)}):", valid_scopes)
print(f"Invalid ({len(invalid_scopes)}):", invalid_scopes)

# Now test all valid ones together
valid_str = " ".join(valid_scopes)
combo_url = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={urllib.parse.quote(valid_str)}"
page.goto(combo_url, wait_until="domcontentloaded", timeout=15000)
print("\nCombined Valid Test URL:", page.url)
if "invalid_scope" not in page.url:
    print("[SUCCESS] ALL VALID SCOPES TOGETHER PASSED!")
    print("WORKING SCOPE STRING:")
    print(f'"{valid_str}"')
