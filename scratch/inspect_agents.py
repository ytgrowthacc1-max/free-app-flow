import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("WHOP_API_KEY")

headers = {"Authorization": f"Bearer {api_key}"}

# Test querying /users/user_X1Uk8voCxS7Vs or /me or /agents
print("=== Inspecting agent user_X1Uk8voCxS7Vs via API Key ===")

url_user = "https://api.whop.com/api/v1/users/user_X1Uk8voCxS7Vs"
res_u = requests.get(url_user, headers=headers, timeout=5)
print(f"GET /users/user_X1Uk8voCxS7Vs -> HTTP {res_u.status_code}: {res_u.text}")

url_app_agents = "https://api.whop.com/api/v1/company/agents"
res_a = requests.get(url_app_agents, headers=headers, timeout=5)
print(f"GET /company/agents -> HTTP {res_a.status_code}: {res_a.text}")
