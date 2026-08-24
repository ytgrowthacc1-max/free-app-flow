import requests
import json

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"
img_bytes = requests.get(avatar_url).content

print("--- Test 1: Multipart file upload to https://api.whop.com/v1/files ---")
r1 = requests.post(
    "https://api.whop.com/v1/files",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": ("avatar.jpg", img_bytes, "image/jpeg")}
)
print("Status:", r1.status_code)
print("Text:", r1.text[:500])

print("\n--- Test 2: JSON payload with filename & mime_type ---")
r2 = requests.post(
    "https://api.whop.com/v1/files",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"filename": "avatar.jpg", "mime_type": "image/jpeg"}
)
print("Status:", r2.status_code)
print("Text:", r2.text[:500])

print("\n--- Test 3: JSON payload with filename & type ---")
r3 = requests.post(
    "https://api.whop.com/v1/files",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"filename": "avatar.jpg", "type": "image/jpeg"}
)
print("Status:", r3.status_code)
print("Text:", r3.text[:500])
