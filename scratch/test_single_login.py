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
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
sys.path.append(r"c:\Python\WHOP AUTOMATION AGENTIC\execution")

import profile_db as db
from auto_authorize import _build_auth_url, _exchange_code_for_token
from browser_manager import BrowserManager
from whop_auth import save_json_atomic

def extract_password(notes):
    if not notes:
        return None
    match = re.search(r"Email Pass:\s*([^\s|]+)", str(notes))
    if match:
        return match.group(1).strip()
    return None

profile_id = "1dda3bd2-1f95-4242-b698-636fb522fa4e" # kqgqfwxz@exartimail.com
p = db.get_profile(profile_id)
email = p.get("name")
password = extract_password(p.get("notes"))

print(f"Target Profile: {email} | Password: {password}")

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
server.timeout = 1

def serve():
    deadline = time.time() + 45
    while captured_code[0] is None and time.time() < deadline:
        server.handle_request()

t = threading.Thread(target=serve, daemon=True)
t.start()

with BrowserManager(p, headless=False) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    print("Navigating to OAuth URL...")
    page.goto(auth_url)
    time.sleep(5)
    
    print("Current URL:", page.url)
    print("Page Title:", page.title())
    
    # Fill email if present
    email_el = page.locator("input[type='email'], input[name='email']").first
    if email_el.count() > 0 and email_el.is_visible():
        print("Filling email...")
        email_el.fill(email)
        time.sleep(1)
        # press Enter
        email_el.press("Enter")
        time.sleep(4)
        
    print("URL after email submit:", page.url)
    
    # Fill password if present
    pass_el = page.locator("input[type='password'], input[name='password']").first
    if pass_el.count() > 0 and pass_el.is_visible():
        print("Filling password...")
        pass_el.fill(password)
        time.sleep(1)
        pass_el.press("Enter")
        time.sleep(6)
        
    print("URL after password submit:", page.url)
    
    # Authorize button check
    for sel in ["button:has-text('Allow')", "button:has-text('Authorize')", "button:has-text('Approve')"]:
        btn = page.locator(sel).first
        if btn.count() > 0 and btn.is_visible():
            print(f"Clicking authorize button: {sel}")
            btn.click()
            time.sleep(5)
            break
            
    time.sleep(5)

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
