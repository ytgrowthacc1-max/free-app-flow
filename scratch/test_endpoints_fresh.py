import requests

endpoints = ['/api/profile_info', '/api/profiles', '/api/experiences']
for ep in endpoints:
    try:
        r = requests.get(f'http://localhost:8080{ep}', timeout=5)
        print(f"[{ep}] Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"  Count: {len(data)}")
            elif isinstance(data, dict):
                print(f"  Keys: {list(data.keys())}")
    except Exception as e:
        print(f"[{ep}] Error: {e}")
