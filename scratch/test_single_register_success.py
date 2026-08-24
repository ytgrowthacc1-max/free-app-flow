import sys
import os
import json
import time
import secrets
import hashlib
import base64
import urllib.parse
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
sys.path.append(r"c:\Python\WHOP AUTOMATION AGENTIC\execution")

import profile_db as db
from auto_authorize import _build_auth_url, _exchange_code_for_token
from browser_manager import BrowserManager
from whop_auth import save_json_atomic

profile_id = "0e69a551-0080-4fc6-a14a-0482a2d10331" # joelrocha1915@apmexbely.com
p = db.get_profile(profile_id)
p["browser_type"] = "camoufox"
email = p.get("name")

print(f"\nTargeting REGISTER SUCCESS Profile: {email} ({profile_id})")

code_verifier = secrets.token_urlsafe(32)
hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')
state = secrets.token_urlsafe(16)
nonce = secrets.token_urlsafe(16)
auth_url = _build_auth_url(code_challenge, state, nonce)

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
            self.wfile.write(b"<h1>Authorized!</h1>")

server = HTTPServer(("localhost", 8000), CallbackHandler)

def serve():
    deadline = time.time() + 60
    while captured_code[0] is None and time.time() < deadline:
        server.handle_request()

t = threading.Thread(target=serve, daemon=True)
t.start()

with BrowserManager(p, headless=False) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    print("Navigating to OAuth Authorization URL...")
    try:
        page.goto(auth_url, wait_until="domcontentloaded", timeout=25000)
    except Exception as e:
        print("Navigation info:", e)
        
    time.sleep(3)
    
    print("Current URL:", page.url)

    if "code=" in (page.url or "") and not captured_code[0]:
        parsed = urllib.parse.urlparse(page.url)
        captured_code[0] = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]

    if not captured_code[0]:
        for sel in ["button:has-text('Allow')", "button:has-text('Authorize')", "button:has-text('Approve')", "button:has-text('Allow access')"]:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible():
                print(f"Clicking authorize button: {sel}")
                btn.click()
                for _ in range(15):
                    time.sleep(1)
                    if captured_code[0] or "code=" in (page.url or ""):
                        print("Code detected after click! URL:", page.url)
                        if not captured_code[0] and "code=" in page.url:
                            parsed = urllib.parse.urlparse(page.url)
                            captured_code[0] = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]
                        break
                break

    if "code=" in (page.url or "") and not captured_code[0]:
        parsed = urllib.parse.urlparse(page.url)
        captured_code[0] = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]

t.join(timeout=2)
code = captured_code[0]
print("CAPTURED CODE:", code)

if code:
    access_token, refresh_token = _exchange_code_for_token(code, code_verifier)
    print("ACCESS TOKEN:", access_token[:30] if access_token else "FAILED")
    if access_token:
        res = requests.get("https://api.whop.com/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}).json()
        b_id = res.get("id")
        b_name = res.get("username")
        print(f"WHOAMI: @{b_name} ({b_id})")
        
        bot_dir = os.path.join(r"c:\Python\WHOP AUTOMATION AGENTIC\profiles\bots", b_id)
        os.makedirs(bot_dir, exist_ok=True)
        save_json_atomic(os.path.join(bot_dir, "profile.json"), {
            "bot_user_id": b_id,
            "bot_username": b_name,
            "email": email,
            "oauth_token": access_token,
            "refresh_token": refresh_token,
            "pinned": True
        })
        print("SAVED PROFILE!")
        
        sync_res = requests.post("http://localhost:8080/api/sync_bot_companies", json={"bot_user_id": b_id}, timeout=15)
        print("SYNC RES:", sync_res.text)
