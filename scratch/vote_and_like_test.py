import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
token = os.getenv("WHOP_OAUTH_TOKEN")
post_id = "post_1Cc8GyP11LHWaXTXFK6Lq1" # From our test poll creation

url = "https://api.whop.com/api/v1/reactions"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Try to vote for option '1'
payload_vote = {
    "resource_id": post_id,
    "poll_option_id": "1"
}

print("Attempting to vote on poll...")
r_vote = requests.post(url, headers=headers, json=payload_vote)
print("Vote status:", r_vote.status_code)
print("Vote response:")
print(r_vote.text)

# 2. Try to like the main post
payload_like = {
    "resource_id": post_id
}
print("\nAttempting to like post...")
r_like = requests.post(url, headers=headers, json=payload_like)
print("Like status:", r_like.status_code)
print("Like response:")
print(r_like.text)
