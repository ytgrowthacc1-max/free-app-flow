import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
post_id = "post_1Cc8GyP11LHWaXTXFK6Lq1" # The poll post we voted on in scratch/vote_and_like_test.py

url = "https://api.whop.com/api/v1/reactions"
headers = {
    "Authorization": f"Bearer {token}"
}
params = {
    "resource_id": post_id
}

r = requests.get(url, headers=headers, params=params)
print("Status:", r.status_code)
if r.status_code == 200:
    res = r.json()
    print("Reactions JSON Response:")
    print(json.dumps(res, indent=2))
else:
    print("Error:", r.text)
