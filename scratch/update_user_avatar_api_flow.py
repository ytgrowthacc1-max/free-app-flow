import requests
import json
import os
import sys

WHOP_AUTOMATION_DIR = r"C:\Python\WHOP AUTOMATION AGENTIC"
sys.path.insert(0, WHOP_AUTOMATION_DIR)

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

access_token = data.get("oauth_token")
print(f"[INFO] Loaded OAuth Access Token for @dawnmuros (len: {len(access_token)})")

avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

# Download image bytes locally
img_res = requests.get(avatar_url)
if img_res.status_code != 200:
    print(f"[ERROR] Failed to download avatar image: status {img_res.status_code}")
    sys.exit(1)

img_bytes = img_res.content
print(f"[INFO] Downloaded avatar image ({len(img_bytes)} bytes)")

WHOP_API = "https://api.whop.com/api/v5"

# Step 1: Create file record
print("\n--- Step 1: POST /files ---")
step1_res = requests.post(
    f"{WHOP_API}/files",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    },
    json={
        "filename": "avatar.jpg",
        "visibility": "public"
    }
)

print("Step 1 Status:", step1_res.status_code)
print("Step 1 Text:", step1_res.text)

if step1_res.status_code not in (200, 201):
    print("[ERROR] Failed to create file record.")
    sys.exit(1)

file_info = step1_res.json()
file_id = file_info.get("id")
upload_url = file_info.get("upload_url")
upload_headers = file_info.get("upload_headers", {})

print(f"\n[SUCCESS] File ID: {file_id}")
print(f"[SUCCESS] Upload URL: {upload_url}")

# Step 2: Upload image bytes to presigned S3 URL
print("\n--- Step 2: PUT presigned S3 URL ---")
headers_s3 = upload_headers if upload_headers else {"Content-Type": "image/jpeg"}
step2_res = requests.put(
    upload_url,
    headers=headers_s3,
    data=img_bytes
)

print("Step 2 Status:", step2_res.status_code)
if step2_res.status_code not in (200, 201, 204):
    print("[ERROR] Failed to upload image to S3:", step2_res.text)
    sys.exit(1)

print("[SUCCESS] Image bytes successfully uploaded to S3!")

# Step 3: Set uploaded file as user's profile picture
print("\n--- Step 3: PATCH /users/me ---")
step3_res = requests.patch(
    f"{WHOP_API}/users/me",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    },
    json={
        "profile_picture": {"id": file_id}
    }
)

print("Step 3 Status:", step3_res.status_code)
print("Step 3 Text:", step3_res.text[:600])

if step3_res.status_code == 200:
    print("\n==========================================")
    print("🎉 SUCCESS! PROFILE PICTURE UPDATED FOR @dawnmuros!")
    print("==========================================")
else:
    print("[ERROR] Failed to update profile picture in Step 3.")
