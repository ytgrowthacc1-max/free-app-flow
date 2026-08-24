import os
import sys
import time
import requests
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

test_scopes = [
    "user:profile:update",
    "user:read",
    "user:update",
    "profile",
    "email",
    "openid",
    "company:create",
    "company:basic:read",
    "experience:create",
    "forum:read",
    "forum:post:create",
    "chat:read",
    "chat:message:create",
    "support_chat:read",
    "support_chat:message:create",
    "dms:read",
    "dms:message:manage"
]

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    valid = []
    invalid = []
    
    for scope in test_scopes:
        auth_url = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={urllib.parse.quote(scope)}"
        page.goto(auth_url, wait_until="domcontentloaded", timeout=15000)
        time.sleep(1)
        curr_url = page.url
        if "invalid_scope" in curr_url:
            print(f"Scope '{scope}' -> INVALID")
            invalid.append(scope)
        else:
            print(f"Scope '{scope}' -> VALID (URL: {curr_url[:80]})")
            valid.append(scope)

print("\n--- Summary ---")
print("Valid Scopes:", valid)
print("Invalid Scopes:", invalid)
