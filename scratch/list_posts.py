import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
exp_id = "exp_RpQSciawxkuJlm"

url = f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

r = requests.get(url, headers=headers)
print("Status:", r.status_code)
if r.status_code == 200:
    res = r.json()
    print("Keys in response:", list(res.keys()))
    if 'data' in res:
        print(f"Data type: {type(res['data'])}, len: {len(res['data'])}")
        if len(res['data']) > 0:
            print("First item keys:", list(res['data'][0].keys()))
            print(json.dumps(res['data'][0], indent=2))
else:
    print("Response:", r.text)
