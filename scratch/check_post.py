import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
post_id = "post_1Cc8CPj2dQmbGCiJt95kr3"

url = f"https://api.whop.com/api/v1/forum_posts/{post_id}"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

r = requests.get(url, headers=headers)
print("Status:", r.status_code)
if r.status_code == 200:
    import json
    print(json.dumps(r.json(), indent=2))
else:
    print("Response:", r.text)
