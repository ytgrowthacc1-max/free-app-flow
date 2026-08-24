import os
import sys
import json
import base64
import time

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
sys.path.insert(0, os.path.join(base_dir, "execution"))

from whop_auth import get_fresh_token, is_token_expired

bots_dir = os.path.join(base_dir, "profiles", "bots")

fresh_bots = []
for b in sorted(os.listdir(bots_dir)):
    bpath = os.path.join(bots_dir, b)
    if not os.path.isdir(bpath):
        continue
    subdirs = [d for d in os.listdir(bpath) if os.path.isdir(os.path.join(bpath, d))]
    comp_dirs = [d for d in subdirs if d.startswith("biz_") or d.startswith("comp_")]
    if len(comp_dirs) == 0:
        pfile = os.path.join(bpath, "profile.json")
        pdata = {}
        if os.path.exists(pfile):
            try:
                pdata = json.load(open(pfile, encoding="utf-8"))
            except Exception:
                pass
        fresh_bots.append((b, pdata))

print(f"Total Fresh Bots: {len(fresh_bots)}")

tested = []
for b, pdata in fresh_bots[:15]:
    uname = pdata.get("bot_username", "unknown")
    token = pdata.get("oauth_token", "")
    refresh_token = pdata.get("refresh_token", "")
    
    scopes = []
    sub = None
    exp = None
    if token:
        try:
            parts = token.split(".")
            if len(parts) == 3:
                payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
                scopes = payload.get("scope", "").split()
                sub = payload.get("sub")
                exp = payload.get("exp")
        except Exception as e:
            scopes = [f"ERR: {e}"]

    # Test getting fresh token
    fresh_res = "N/A"
    try:
        t = get_fresh_token(b, prevent_auto_auth=True)
        if t:
            fresh_res = f"VALID (sub={sub})"
        else:
            fresh_res = "FAILED (None returned)"
    except Exception as te:
        fresh_res = f"ERR: {te}"

    print(f"Bot: {b} (@{uname}) | Scopes: {scopes} | Status: {fresh_res}")
