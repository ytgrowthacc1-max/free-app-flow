import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
post_id = "post_1Cc8HYphqiMJc5NKqLhKxQ"

url = f"https://api.whop.com/api/v1/forum_posts/{post_id}"
headers = {
    "Authorization": f"Bearer {token}"
}
params = {
    "experience_id": "exp_RpQSciawxkuJlm"
}

r = requests.get(url, headers=headers, params=params)
print("Status:", r.status_code)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    print("Error:", r.text)
