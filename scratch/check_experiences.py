import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("WHOP_OAUTH_TOKEN")
company_id = os.getenv("WHOP_COMPANY_ID")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Try fetching experiences directly
url = f"https://api.whop.com/api/v1/experiences?company_id={company_id}"
r = requests.get(url, headers=headers)
print("Experiences status:", r.status_code)
print("Experiences response:", r.text)
