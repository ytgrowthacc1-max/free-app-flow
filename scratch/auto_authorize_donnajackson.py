import os
import sys
import time
import secrets
import hashlib
import base64
import urllib.parse
import json

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
try:
    import profile_db as db
    from browser_manager import BrowserManager

    whop_profiles = db.list_profiles(platform="whop")
    print(f"Found {len(whop_profiles)} Whop browser profiles.")
    target_prof = None
    for p in whop_profiles:
        p_str = str(p).lower()
        if "donnajacksona7" in p_str or "dona" in p_str:
            target_prof = p
            break
            
    if not target_prof and whop_profiles:
        print("donnajacksona7 not explicitly found by name. Profiles available:")
        for p in whop_profiles:
            print(" -", p.get("account_number"), p.get("name"), p.get("username"))
            
    if target_prof:
        print(f"Found target browser profile: {target_prof.get('name')} ({target_prof.get('username')})")
        client_id = "app_oPIxXnyEJ8uxNK"
        redirect_uri = "http://localhost:8000/callback"
        code_verifier = secrets.token_urlsafe(32)
        hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')

        scopes = "openid profile email company:create company:basic:read user:profile:update experience:create app_authorization:create forum:read forum:post:create chat:read chat:message:create support_chat:read support_chat:message:create dms:read dms:message:manage"
        oauth_state = secrets.token_urlsafe(16)
        oauth_nonce = secrets.token_urlsafe(16)

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scopes,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": oauth_state,
            "nonce": oauth_nonce
        }
        auth_url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)

        import requests
        with BrowserManager(target_prof, headless=True) as browser:
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(auth_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
            
            for selector in ["button:has-text('Allow')", "button:has-text('Authorize')", "button:has-text('Allow access')", "button[type='submit']"]:
                btn = page.locator(selector).first
                if btn.count() > 0 and btn.is_visible():
                    print(f"Clicking authorization button: {selector}")
                    btn.click()
                    time.sleep(5)
                    break
                    
            if "callback?code=" in page.url:
                parsed = urllib.parse.urlparse(page.url)
                qs = urllib.parse.parse_qs(parsed.query)
                code = qs.get("code", [None])[0]
                token_res = requests.post(
                    "https://api.whop.com/oauth/token",
                    data={
                        "client_id": client_id,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "code_verifier": code_verifier
                    }
                )
                if token_res.status_code == 200:
                    token_json = token_res.json()
                    out_file = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_gAkQk98I3AyP4\profile.json"
                    with open(out_file, "w", encoding="utf-8") as f:
                        json.dump({
                            "bot_user_id": "user_gAkQk98I3AyP4",
                            "bot_username": "donnajacksona7",
                            "oauth_token": token_json.get("access_token"),
                            "refresh_token": token_json.get("refresh_token")
                        }, f, indent=2)
                    print("[SUCCESS] Obtained new token with company:create scope and updated profile.json!")

except Exception as e:
    print("Error during auto-authorization:", e)
