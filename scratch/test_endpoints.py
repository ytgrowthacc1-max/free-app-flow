import requests
import json

try:
    r = requests.get("http://localhost:8080/api/profile_info", timeout=5)
    print("GET /api/profile_info status:", r.status_code)
    print("GET /api/profile_info response:")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print("Failed to GET /api/profile_info:", e)

print("-" * 50)

try:
    r = requests.get("http://localhost:8080/api/profiles", timeout=5)
    print("GET /api/profiles status:", r.status_code)
    print("GET /api/profiles response:")
    print(json.dumps(r.json()[:2], indent=2)) # Print first two profiles
except Exception as e:
    print("Failed to GET /api/profiles:", e)
