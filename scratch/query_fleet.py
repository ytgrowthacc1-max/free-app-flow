import urllib.request
import json

for port in [8000, 5000, 5050, 3000, 8080]:
    try:
        url = f"http://127.0.0.1:{port}/api/fleet-summary"
        req = urllib.request.urlopen(url, timeout=3)
        data = json.loads(req.read().decode('utf-8'))
        print(f"Dashboard found on port {port}!")
        print(f"Summary: {data.get('summary')}")
        comms = data.get("communities", [])
        print(f"Total communities: {len(comms)}")
        needs_att = [c for c in comms if c.get("needs_attention")]
        print(f"Total needs_attention: {len(needs_att)}")
        for c in needs_att:
            print(f"  - Bot: {c.get('bot_handle')} ({c.get('bot_user_id')}) | Comp: {c.get('company_name')} | Pinned: {c.get('is_pinned')} | Sched: {c.get('scheduler_enabled')} | TokenValid: {c.get('token_valid')} | Idle: {c.get('idle_minutes')}m | Hidden: {c.get('is_hidden')}")
        break
    except Exception as e:
        # print(f"Port {port} error: {e}")
        pass
