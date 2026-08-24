import urllib.request
import json

try:
    req = urllib.request.urlopen("http://localhost:8080/api/fleet/summary", timeout=5)
    data = json.loads(req.read().decode('utf-8'))
    print("Success loading fleet summary from live server!")
    print("Summary stats:", json.dumps(data.get("summary"), indent=2))
    pinned = [c for c in data.get("communities", []) if c.get("is_pinned") and not c.get("is_hidden")]
    print(f"Total pinned communities: {len(pinned)}")
    needs_att = [c for c in pinned if c.get("needs_attention")]
    print(f"Total pinned needs_attention: {len(needs_att)}")
    for c in needs_att:
        print(f"  - Bot: {c.get('bot_handle')} | Comp: {c.get('company_name')} | Idle: {c.get('idle_minutes')}m | TokenValid: {c.get('token_valid')}")
except Exception as e:
    print(f"Error: {e}")
