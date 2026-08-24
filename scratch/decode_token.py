import json
import os
import base64
import time

pfile = r"profiles/bots/user_7ziL4hNckh6Ei/profile.json"
with open(pfile, "r") as f:
    pdata = json.load(f)

token = pdata.get("oauth_token")
print("Token:", token[:30] + "...")

parts = token.split('.')
payload_b64 = parts[1]
payload_b64 += '=' * (-len(payload_b64) % 4)
payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))

print("Subject (user_id):", payload.get("sub"))
print("Expiration timestamp:", payload.get("exp"))
print("Current system time:", time.time())
print("Expires in (seconds):", payload.get("exp") - time.time())
print("Is expired?", (payload.get("exp") - time.time()) < 300)
