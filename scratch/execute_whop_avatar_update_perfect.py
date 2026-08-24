import requests
import json
import sys
import time

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"
with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

token = data.get("oauth_token")
avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

print(f"[INFO] Loaded OAuth Access Token for @dawnmuros (len: {len(token)})")

# Download image bytes
img_res = requests.get(avatar_url)
if img_res.status_code != 200:
    print(f"[ERROR] Could not download image: status {img_res.status_code}")
    sys.exit(1)

img_bytes = img_res.content
print(f"[INFO] Downloaded avatar image ({len(img_bytes)} bytes)")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# STEP 1: Create file record via POST /v1/files
print("\n--- STEP 1: Create File Record (POST https://api.whop.com/v1/files) ---")
step1_res = requests.post(
    "https://api.whop.com/v1/files",
    headers=headers,
    json={
        "filename": "dawnmuros_avatar.jpg"
    }
)

print("Step 1 Status:", step1_res.status_code)
if step1_res.status_code != 200:
    print("[ERROR] Failed Step 1:", step1_res.text)
    sys.exit(1)

file_info = step1_res.json()
file_id = file_info.get("id")
upload_url = file_info.get("upload_url")
upload_headers = file_info.get("upload_headers", {"Content-Type": "image/jpeg"})

print(f"\n[SUCCESS] Generated File ID: {file_id}")
print(f"[SUCCESS] Presigned S3 Upload URL: {upload_url}")

# STEP 2: Upload image bytes to presigned S3 URL via PUT
print("\n--- STEP 2: Upload Image to S3 (PUT upload_url) ---")
step2_res = requests.put(
    upload_url,
    headers=upload_headers,
    data=img_bytes
)

print("Step 2 Status:", step2_res.status_code)
if step2_res.status_code not in (200, 201, 204):
    print("[ERROR] Failed S3 Upload:", step2_res.text)
    sys.exit(1)

print("[SUCCESS] Image bytes successfully uploaded to S3!")

# STEP 2.5: Poll file status until upload_status == 'completed'
print("\n--- STEP 2.5: Polling File Processing Status ---")
file_status = "pending"
for i in range(15):
    time.sleep(2)
    check_res = requests.get(f"https://api.whop.com/v1/files/{file_id}", headers=headers)
    if check_res.status_code == 200:
        cdata = check_res.json()
        file_status = cdata.get("upload_status")
        print(f"  Attempt {i+1}: upload_status = '{file_status}'")
        if file_status in ("ready", "completed"):
            break
    else:
        print(f"  Attempt {i+1}: GET file status {check_res.status_code}")

if file_status != "completed":
    print(f"[WARNING] File processing status is still '{file_status}', proceeding with PATCH...")

# STEP 3: Update profile picture via PATCH /v1/users/me
print("\n--- STEP 3: Update User Profile Picture (PATCH https://api.whop.com/v1/users/me) ---")
step3_res = requests.patch(
    "https://api.whop.com/v1/users/me",
    headers=headers,
    json={
        "profile_picture": {"id": file_id}
    }
)

print("Step 3 Status:", step3_res.status_code)
print("Step 3 Response:", step3_res.text)

if step3_res.status_code == 200:
    print("\n=======================================================")
    print("🎉 SUCCESS! PROFILE PICTURE FULLY UPDATED FOR @dawnmuros!")
    print("=======================================================")
else:
    print("[ERROR] Failed Step 3 profile update.")
