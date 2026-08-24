import requests
try:
    r = requests.get("http://localhost:8080/api/history", timeout=2)
    print("Server is active. Status:", r.status_code)
except Exception as e:
    print("Server is offline:", e)
