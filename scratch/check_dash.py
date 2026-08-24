import requests
try:
    resp = requests.get("http://localhost:8080/")
    print(f"Status: {resp.status_code}")
    print(resp.text[:200])
except Exception as e:
    print(f"Error: {e}")
