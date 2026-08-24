import os
import sys
import time
import secrets
import hashlib
import base64
import urllib.parse
import json
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "execution"))
from app_config import get_whop_app_credentials

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

# ── Target account ──────────────────────────────────────────────────────────
TARGET_WHOP_USERNAME = "donnajacksona7"
BOT_USER_ID          = "user_gAkQk98I3AyP4"
BOT_PROFILE_JSON     = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_gAkQk98I3AyP4\profile.json"

profile = None
for p in db.list_profiles(platform="whop"):
    if TARGET_WHOP_USERNAME.lower() in str(p.get("whop_username", "")).lower() \
       or TARGET_WHOP_USERNAME.lower() in str(p.get("name", "")).lower():
        profile = p
        break

if not profile:
    print(f"[ERROR] Could not find browser profile for {TARGET_WHOP_USERNAME}")
    sys.exit(1)

print(f"[INFO] Found browser profile: {profile.get('name')} (account #{profile.get('account_number')})")

# Temporarily mark the profile as running so BrowserManager doesn't skip it
profile["status"] = "running"

# ── Local callback server to catch the OAuth redirect ────────────────────────
captured_code = [None]

class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): return
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        if code:
            captured_code[0] = code
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorized!</h1><p>Close this tab.</p>")
        else:
            self.send_response(400)
            self.end_headers()

def run_callback_server():
    try:
        server = HTTPServer(("localhost", 8000), CallbackHandler)
        server.timeout = 1
        deadline = time.time() + 45
        while captured_code[0] is None and time.time() < deadline:
            server.handle_request()
    except OSError as e:
        print(f"[WARN] Callback server error: {e}")

server_thread = threading.Thread(target=run_callback_server, daemon=True)
server_thread.start()

# ── PKCE + OAuth URL ─────────────────────────────────────────────────────────
client_id, client_secret, redirect_uri = get_whop_app_credentials("app_oPIxXnyEJ8uxNK")
print(f"[INFO] Using App ID: {client_id}, Redirect: {redirect_uri}")

code_verifier = secrets.token_urlsafe(32)
hash_bytes    = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(hash_bytes).decode("utf-8").replace("=", "")

scopes = (
    "openid profile email "
    "company:create company:basic:read "
    "experience:create "
    "forum:read forum:post:create "
    "chat:read chat:message:create "
    "support_chat:read support_chat:message:create "
    "dms:read dms:message:manage"
)
oauth_state = secrets.token_urlsafe(16)
oauth_nonce = secrets.token_urlsafe(16)

params = {
    "client_id"             : client_id,
    "redirect_uri"          : redirect_uri,
    "response_type"         : "code",
    "scope"                 : scopes,
    "code_challenge"        : code_challenge,
    "code_challenge_method" : "S256",
    "state"                 : oauth_state,
    "nonce"                 : oauth_nonce,
}
auth_url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
print(f"[INFO] Auth URL:\n{auth_url}\n")

# ── Launch browser and click Allow ───────────────────────────────────────────
with BrowserManager(profile, headless=False) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()

    print("[INFO] Navigating to authorization URL...")
    page.goto(auth_url, wait_until="domcontentloaded", timeout=35000)
    time.sleep(4)

    print("Current URL :", page.url)
    try:
        print("Page Title  :", page.title())
    except Exception:
        print("Page Title  : (navigated away)")

    try:
        btns = page.locator("button, a[role='button'], input[type='submit']").all_inner_texts()
        print("Buttons found:", btns)
    except Exception:
        btns = []
        print("Buttons found: (navigated)")

    # Click the authorize button
    for selector in [
        "button:has-text('Allow')",
        "button:has-text('Authorize')",
        "button:has-text('Allow access')",
        "button:has-text('Approve')",
        "button:has-text('Continue')",
        "button[type='submit']",
    ]:
        try:
            btn = page.locator(selector).first
            if btn.count() > 0 and btn.is_visible():
                print(f"[INFO] Clicking: {selector}")
                btn.click()
                time.sleep(5)
                break
        except Exception:
            pass

    # Wait for callback server to catch the redirect
    print("[INFO] Waiting for OAuth callback redirect...")
    for _ in range(20):
        if captured_code[0]:
            break
        time.sleep(1)

    print("URL after click:", page.url)
    code = captured_code[0]

    # Fallback: try to read code from page URL directly
    if not code and "callback?code=" in page.url:
        parsed = urllib.parse.urlparse(page.url)
        code = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]

    if code:
        print(f"[SUCCESS] Captured code: {code[:20]}...")

        # Exchange code for tokens
        token_res = requests.post(
            "https://api.whop.com/oauth/token",
            data={
                "client_id"     : client_id,
                "client_secret" : client_secret,
                "grant_type"    : "authorization_code",
                "code"          : code,
                "redirect_uri"  : redirect_uri,
                "code_verifier" : code_verifier,
            },
            timeout=15,
        )
        print(f"Token exchange: {token_res.status_code}")
        if token_res.status_code == 200:
            tdata         = token_res.json()
            access_token  = tdata.get("access_token")
            refresh_token = tdata.get("refresh_token")

            # Save to profile.json
            if os.path.exists(BOT_PROFILE_JSON):
                with open(BOT_PROFILE_JSON, "r", encoding="utf-8") as f:
                    pjson = json.load(f)
                pjson["oauth_token"]  = access_token
                pjson["refresh_token"] = refresh_token
                pjson.pop("refresh_token_invalid", None)
                with open(BOT_PROFILE_JSON, "w", encoding="utf-8") as f:
                    json.dump(pjson, f, indent=2)
            print("[SUCCESS] Saved fresh token to profile.json!")
            print("New token preview:", access_token[:40], "...")
        else:
            print("[ERROR] Token exchange failed:", token_res.text[:300])
    else:
        print("[WARNING] No authorization code captured.")
        print("Current page URL:", page.url)
        print("Try running oauth_helper.py manually: python execution/oauth_helper.py")
