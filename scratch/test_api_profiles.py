import requests
import json

try:
    r = requests.get('http://localhost:8080/api/profiles', timeout=5)
    print("Status code:", r.status_code)
    data = r.json()
    print("Profiles returned count:", len(data))
    for p in data:
        print(f" - Bot: {p.get('bot_username')} ({p.get('bot_user_id')}), status: {p.get('status')}, hidden: {p.get('hidden')}, companies count: {len(p.get('companies', []))}")
except Exception as e:
    print("Error querying /api/profiles:", e)
