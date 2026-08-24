import requests

url = "http://127.0.0.1:8000/callback"
params = {
    "code": "ecd13ce7de36026a4dcd2cc9fffd14a52a6ee3ad34bee9465c395c37d032ca73",
    "state": "Ecy-JJq_mWq2iYOoWRMZRQ"
}

print(f"[INFO] Sending GET request to local server: {url}...")
try:
    r = requests.get(url, params=params)
    print(f"[STATUS] {r.status_code}")
    print(r.text)
except Exception as e:
    print(f"[ERROR] Request failed: {e}")
