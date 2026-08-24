import requests

try:
    r = requests.get("http://localhost:3000/", timeout=2)
    print(f"Port 3000 status: {r.status_code}")
except Exception as e:
    print(f"Port 3000 is NOT running ({e})")
