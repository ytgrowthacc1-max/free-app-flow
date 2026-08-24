import requests
import urllib.parse
import secrets
import hashlib
import base64

client_id = "app_oPIxXnyEJ8uxNK"
redirect_uri = "http://localhost:8000/callback"

test_scopes_list = [
    "openid profile email company:create company:basic:read user:profile:update",
    "profile email company:create company:basic:read experience:create forum:read forum:post:create chat:read chat:message:create support_chat:read support_chat:message:create dms:read dms:message:manage user:profile:update"
]

session = requests.Session()

for scope in test_scopes_list:
    code_verifier = secrets.token_urlsafe(32)
    hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')
    nonce = secrets.token_urlsafe(16)
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": "test12345",
        "nonce": nonce
    }
    
    url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
    r = session.get(url, allow_redirects=False)
    loc = r.headers.get("Location", "")
    print(f"\nScope: {scope[:60]}...")
    print("HTTP Status:", r.status_code)
    print("Redirect Location:", loc)
    if "error" in loc:
        parsed = urllib.parse.urlparse(loc)
        qs = urllib.parse.parse_qs(parsed.query)
        print("  -> ERROR TYPE:", qs.get("error"))
        print("  -> ERROR DESC:", qs.get("error_description"))
    else:
        print("  -> SUCCESS! (Proceeds to login/authorization page)")
