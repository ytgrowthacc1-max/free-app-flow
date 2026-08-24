import requests

try:
    r = requests.get("http://localhost:8085/", timeout=2)
    print(f"Port 8085 status: {r.status_code}")
except Exception as e:
    print(f"Port 8085 is NOT running ({e})")
