import os
import requests
import json

# Load credentials from .env
env_vars = {}
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()

whop_api_key = env_vars.get("WHOP_API_KEY", "")
whop_oauth_token = env_vars.get("WHOP_OAUTH_TOKEN", "")

url = "https://api.whop.com/api/v1/companies"
payload = {
    "title": "Leaderboard App Community",
    "description": "Community promoting the Leaderboard application",
    "send_customer_emails": False
}

print("--- Testing API Token Access ---")

# Test 1: Testing with WHOP_OAUTH_TOKEN
if whop_oauth_token:
    print("\n1. Testing with WHOP_OAUTH_TOKEN...")
    headers = {
        "Authorization": f"Bearer {whop_oauth_token}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

# Test 2: Testing with WHOP_API_KEY
if whop_api_key:
    print("\n2. Testing with WHOP_API_KEY...")
    headers = {
        "Authorization": f"Bearer {whop_api_key}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")
