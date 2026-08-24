import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "execution"))

import requests
from dotenv import load_dotenv

load_dotenv()

# Test Flask app before_request auth handling directly with test client
from dashboard_server import app

client = app.test_client()

print("1. Testing unauthorized GET / (should return 401 Unauthorized)...")
res = client.get('/')
print(f"Status Code: {res.status_code}")
print(f"WWW-Authenticate Header: {res.headers.get('WWW-Authenticate')}")

print("\n2. Testing GET / with invalid credentials (should return 401)...")
res_bad = client.get('/', headers={'Authorization': 'Basic d3Jvbmc6d3Jvbmc='})
print(f"Status Code: {res_bad.status_code}")

print("\n3. Testing GET / with VALID credentials (should return 200 OK)...")
import base64
creds = base64.b64encode(b"admin:whopautomation").decode('ascii')
res_good = client.get('/', headers={'Authorization': f'Basic {creds}'})
print(f"Status Code: {res_good.status_code}")
if res_good.status_code == 200:
    print("[SUCCESS] Password authentication verified!")
else:
    print(f"[FAIL] Unexpected status code: {res_good.status_code}")
