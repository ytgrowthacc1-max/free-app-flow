"""
get_outreach_oauth_token.py
────────────────────────────
One-time helper: launches the outreach account's browser (using its existing
cookies), navigates to the Whop OAuth authorization URL, intercepts the
redirect callback, exchanges the code for an access + refresh token, and
saves everything to chatbot_settings.json as an "outreach_accounts" entry.

Run once; after that the dashboard sync loop will automatically pick up
chats from this account.

Usage:
    python scratch/get_outreach_oauth_token.py
"""

import os
import sys
import json
import hashlib
import secrets
import base64
import requests
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from dotenv import load_dotenv

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "execution"))
sys.path.insert(0, str(Path("c:/Python/Browsing Skill Agent/execution")))
load_dotenv(BASE_DIR / ".env")

import profile_db as db
from browser_manager import BrowserManager

# ── Config ────────────────────────────────────────────────────────────────────
EMAIL         = "margaretmerrill1980@radiochemail.ru"
CLIENT_ID     = os.getenv("WHOP_APP_ID",  "app_oPIxXnyEJ8uxNK")
CLIENT_SECRET = os.getenv("WHOP_API_KEY")          # App API key acts as secret
REDIRECT_URI  = "http://localhost:8000/callback"
LABEL         = "margaret_outreach"
SETTINGS_PATH = BASE_DIR / "chatbot_settings.json"

SCOPES = (
    "forum:post:create forum:read chat:read chat:message:create "
    "support_chat:read support_chat:message:create experience:create "
    "company:basic:read dms:read dms:message:manage"
)

# ── PKCE helpers ──────────────────────────────────────────────────────────────
def pkce_pair():
    verifier  = secrets.token_urlsafe(32)
    digest    = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge

# ── Tiny local callback server ────────────────────────────────────────────────
captured_code = [None]

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        captured_code[0] = qs.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Auth captured! You may close this tab.</h2>")
    def log_message(self, *_):
        pass

def run_callback_server():
    srv = HTTPServer(("localhost", 8000), CallbackHandler)
    srv.timeout = 120
    srv.handle_request()   # handle exactly one request then exit

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # 1. Load profile
    profiles = db.list_profiles(platform="whop", search=EMAIL)
    profile  = next((p for p in profiles if p["name"].lower() == EMAIL.lower()), None)
    if not profile:
        print(f"[ERROR] Profile '{EMAIL}' not found in DB.")
        sys.exit(1)
    print(f"[OK] Loaded profile: {profile['name']}  (browser: {profile['browser_type']})")

    # 2. Build auth URL
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(16)
    auth_url = (
        f"https://api.whop.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={requests.utils.quote(REDIRECT_URI, safe='')}"
        f"&response_type=code"
        f"&code_challenge={challenge}"
        f"&code_challenge_method=S256"
        f"&state={state}"
        f"&scope={requests.utils.quote(SCOPES, safe='')}"
    )

    # 3. Start callback listener
    server_thread = threading.Thread(target=run_callback_server, daemon=True)
    server_thread.start()
    print("[INFO] Callback listener started on http://localhost:8000/callback")

    # 4. Open browser with outreach profile → navigate to auth URL
    print("[INFO] Launching browser with outreach profile…")
    mgr = BrowserManager(profile)
    with mgr as browser_ctx:
        page = browser_ctx.new_page()
        page.goto(auth_url)
        print("[INFO] Navigated to Whop OAuth page. Waiting for user to authorise…")

        # Wait up to 90 s for the callback to be hit
        for _ in range(90):
            if captured_code[0]:
                break
            time.sleep(1)

    if not captured_code[0]:
        print("[ERROR] No auth code received within timeout.")
        sys.exit(1)

    code = captured_code[0]
    print(f"[OK] Received auth code: {code[:20]}…")

    # 5. Exchange code for tokens
    resp = requests.post("https://api.whop.com/oauth/token", json={
        "grant_type":    "authorization_code",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri":  REDIRECT_URI,
        "code":          code,
        "code_verifier": verifier,
    })
    if resp.status_code != 200:
        print(f"[ERROR] Token exchange failed: {resp.status_code} – {resp.text}")
        sys.exit(1)

    tok = resp.json()
    access_token  = tok["access_token"]
    refresh_token = tok.get("refresh_token", "")
    print(f"[OK] Access token received: {access_token[:30]}…")

    # 6. Get the bot_user_id from the token itself (decode JWT payload)
    import base64 as _b64, json as _json
    payload_b64 = access_token.split(".")[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)
    payload = _json.loads(_b64.urlsafe_b64decode(payload_b64))
    bot_user_id = payload.get("sub", "")
    print(f"[OK] bot_user_id from token: {bot_user_id}")

    # 7. Merge into chatbot_settings.json → outreach_accounts
    settings = {}
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = _json.load(f)

    outreach_accounts = settings.get("outreach_accounts", [])
    # Remove existing entry for same label
    outreach_accounts = [a for a in outreach_accounts if a.get("label") != LABEL]
    outreach_accounts.append({
        "label":         LABEL,
        "email":         EMAIL,
        "bot_user_id":   bot_user_id,
        "oauth_token":   access_token,
        "refresh_token": refresh_token,
    })
    settings["outreach_accounts"] = outreach_accounts

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        _json.dump(settings, f, indent=2)

    print(f"\n[SUCCESS] Outreach account '{LABEL}' saved to chatbot_settings.json.")
    print("The dashboard will now sync support chats from this account automatically.")
    print("Restart the dashboard server to apply immediately.")

if __name__ == "__main__":
    main()
