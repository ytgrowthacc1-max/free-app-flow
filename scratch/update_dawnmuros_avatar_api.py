import requests
import json
import os

profile_path = r"C:\Python\WHOP AUTOMATION AGENTIC\profiles\bots\user_lO14mFc5tBKN3\profile.json"

with open(profile_path, "r", encoding="utf-8") as f:
    data = json.load(f)

access_token = data.get("oauth_token")
print(f"[INFO] Loaded fresh access token for @dawnmuros (len: {len(access_token)})")

avatar_url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("\n--- 1. Trying PATCH https://api.whop.com/api/v5/users/me ---")
p1 = {"profile_pic_url": avatar_url}
r1 = requests.patch("https://api.whop.com/api/v5/users/me", headers=headers, json=p1)
print("Response Status:", r1.status_code)
print("Response Text:", r1.text[:500])

if r1.status_code != 200:
    print("\n--- 2. Trying PATCH https://api.whop.com/api/v5/me ---")
    r2 = requests.patch("https://api.whop.com/api/v5/me", headers=headers, json=p1)
    print("Response Status:", r2.status_code)
    print("Response Text:", r2.text[:500])

if r1.status_code != 200 and r2.status_code != 200:
    print("\n--- 3. Trying POST upload file to Whop files endpoint ---")
    img_resp = requests.get(avatar_url)
    if img_resp.status_code == 200:
        img_bytes = img_resp.content
        files = {'file': ('avatar.jpg', img_bytes, 'image/jpeg')}
        f_headers = {"Authorization": f"Bearer {access_token}"}
        f_resp = requests.post("https://api.whop.com/api/v5/files", headers=f_headers, files=files)
        print("File Upload Status:", f_resp.status_code)
        print("File Upload Text:", f_resp.text[:500])
        if f_resp.status_code in (200, 201):
            file_data = f_resp.json()
            file_url = file_data.get("url") or file_data.get("id")
            print("Uploaded File URL:", file_url)
            p3 = {"profile_pic_url": file_url}
            r3 = requests.patch("https://api.whop.com/api/v5/users/me", headers=headers, json=p3)
            print("Profile update status with file URL:", r3.status_code)
            print("Profile update text:", r3.text[:500])
