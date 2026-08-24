import os
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

fresh_bots = []
for b in sorted(os.listdir(bots_dir)):
    bpath = os.path.join(bots_dir, b)
    if not os.path.isdir(bpath):
        continue
    subdirs = [d for d in os.listdir(bpath) if os.path.isdir(os.path.join(bpath, d))]
    comp_dirs = [d for d in subdirs if d.startswith("biz_") or d.startswith("comp_")]
    if len(comp_dirs) == 0:
        username = "unknown"
        uinfo = os.path.join(bpath, "user_info.json")
        if os.path.exists(uinfo):
            try:
                username = json.load(open(uinfo, encoding="utf-8")).get("username", "unknown")
            except Exception:
                pass
        otoken = os.path.join(bpath, "oauth_tokens.json")
        token_info = "NO TOKEN"
        scope_info = "N/A"
        if os.path.exists(otoken):
            try:
                td = json.load(open(otoken, encoding="utf-8"))
                has_rf = bool(td.get("refresh_token"))
                scopes = td.get("scope", "")
                token_info = f"Token (has refresh_token={has_rf})"
                scope_info = f"Scopes: {scopes}"
                if username == "unknown":
                    username = td.get("username", "unknown")
            except Exception:
                pass
        fresh_bots.append((b, username, token_info, scope_info))

print(f"Total Fresh Bots (0 communities): {len(fresh_bots)}")
for idx, (bid, uname, tinfo, sinfo) in enumerate(fresh_bots, 1):
    print(f"{idx:2d}. {bid:20s} | @{uname:20s} | {tinfo} | {sinfo}")
