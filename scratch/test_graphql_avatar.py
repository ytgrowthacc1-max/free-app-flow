import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test 1: GraphQL directUpload mutation
query1 = """
mutation createDirectUpload($input: DirectUploadInput!) {
  createDirectUpload(input: $input) {
    directUpload {
      url
      headers
      signedBlobId
    }
  }
}
"""
vars1 = {
  "input": {
    "filename": "avatar.jpg",
    "contentType": "image/jpeg",
    "byteSize": 95569,
    "checksum": "123456"
  }
}

for endpoint in ["https://api.whop.com/graphql", "https://whop.com/api/graphql"]:
    r = requests.post(endpoint, headers=headers, json={"query": query1, "variables": vars1})
    print(f"GraphQL {endpoint} Status:", r.status_code)
    print("Response:", r.text[:500])
