import requests
import sys

print("Testing /api/profile_info...")
try:
    r = requests.get('http://localhost:8080/api/profile_info', timeout=3)
    print("profile_info:", r.status_code, r.text[:100])
except Exception as e:
    print("profile_info error:", e)

print("Testing /api/profiles...")
try:
    r = requests.get('http://localhost:8080/api/profiles', timeout=3)
    print("profiles:", r.status_code, len(r.json()))
except Exception as e:
    print("profiles error:", e)

print("Testing /api/experiences...")
try:
    r = requests.get('http://localhost:8080/api/experiences', timeout=3)
    print("experiences:", r.status_code, r.text[:100])
except Exception as e:
    print("experiences error:", e)
