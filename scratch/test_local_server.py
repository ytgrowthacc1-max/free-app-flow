import requests

try:
    r = requests.get("http://127.0.0.1:5000/api/profiles", timeout=3)
    print(f"[SERVER GET /api/profiles] Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Total profiles returned: {len(data.get('profiles', []))}")
        for p in data.get('profiles', [])[:5]:
            print(f"  - {p.get('bot_username')} ({p.get('bot_user_id')}): status={p.get('status')}")
except Exception as e:
    print(f"[SERVER ERROR] {e}")
