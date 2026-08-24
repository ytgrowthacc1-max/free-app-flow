import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "execution"))
from whop_auth import get_fresh_token

bot_id = "user_P5obcMW3vIrZ8"
oauth_token = get_fresh_token(bot_id)
company_api_key = "apik_B1NebyOXYBzKN_C5278363_C_e87c802459f00113af000bdab2d146d68d7396adb1118abfb7977ade03a0ba"
company_id = "biz_Vwsite2gfnFBU2"

print("--- Testing GraphQL for Members with Country / GeoIP ---")

graphql_urls = [
    "https://api.whop.com/graphql",
    "https://whop.com/api/graphql",
    "https://data.whop.com/graphql"
]

tokens = [
    ("OAuth Token", oauth_token),
    ("Company API Key", company_api_key)
]

# Query 1: Introspect Member fields or query company members
query1 = """
query GetCompanyMembers($companyId: ID!) {
  company(id: $companyId) {
    id
    title
    members(first: 5) {
      edges {
        node {
          id
          createdAt
          user {
            id
            username
            email
          }
        }
      }
    }
  }
}
"""

query2 = """
query GetMemberDetails($id: ID!) {
  member(id: $id) {
    id
    country
    countryCode
    location
    city
    ipAddress
    user {
      id
      username
      email
    }
  }
}
"""

for url in graphql_urls:
    for t_name, token in tokens:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        print(f"\nTarget: {url} | Auth: {t_name}")
        try:
            r = requests.post(url, json={"query": query1, "variables": {"companyId": company_id}}, headers=headers, timeout=5)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print("Response:", json.dumps(r.json(), indent=2)[:500])
            else:
                print("Response:", r.text[:200])
        except Exception as e:
            print(f"Error: {e}")
