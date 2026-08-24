import os
import requests
import json
import time
from dotenv import load_dotenv

# Import auth helper from execution directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from execution.whop_auth import get_fresh_token

def safe_print(text):
    print(text.encode('ascii', 'replace').decode('ascii'))

def main():
    load_dotenv()
    
    # Load credentials
    api_key = os.getenv("WHOP_API_KEY")
    company_id = os.getenv("WHOP_COMPANY_ID")
    
    if not api_key:
        safe_print("[ERROR] WHOP_API_KEY must be set in your .env file.")
        return
    if not company_id:
        safe_print("[ERROR] WHOP_COMPANY_ID must be set in your .env file.")
        return

    try:
        user_token = get_fresh_token()
        safe_print(f"[INFO] Successfully retrieved fresh OAuth token.")
    except Exception as e:
        safe_print(f"[ERROR] Failed to get OAuth token: {e}")
        return

    # Headers using user OAuth token
    user_headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    # 1. Create the file record via Whop POST /files
    files_url = "https://api.whop.com/api/v1/files"
    file_payload = {
        "filename": "poll_test_file.txt",
        "visibility": "public"
    }
    
    safe_print(f"[INFO] Creating file record via POST {files_url}...")
    files_resp = requests.post(files_url, headers=user_headers, json=file_payload)
    if files_resp.status_code not in [200, 201]:
        safe_print(f"[ERROR] Failed to create file: {files_resp.status_code} - {files_resp.text}")
        return

    file_data = files_resp.json()
    file_id = file_data.get("id")
    upload_url = file_data.get("upload_url")

    safe_print(f"[SUCCESS] Created file record. ID: {file_id}")

    # 2. Upload content to S3 using PUT to upload_url
    file_content = "This is a simple file to test how long it takes to process the upload on Whop."
    safe_print(f"[INFO] Uploading content to S3...")
    
    upload_resp = requests.put(upload_url, data=file_content, headers={"Content-Type": "text/plain"})
    if upload_resp.status_code not in [200, 201, 204]:
        safe_print(f"[ERROR] Failed to upload content to S3: {upload_resp.status_code} - {upload_resp.text}")
        return
    safe_print(f"[SUCCESS] File contents uploaded to S3.")

    # 3. Poll GET /files/{file_id}
    detail_url = f"https://api.whop.com/api/v1/files/{file_id}"
    safe_print(f"[INFO] Starting poll of GET {detail_url}...")
    
    for i in range(15):
        time.sleep(1)
        resp = requests.get(detail_url, headers=user_headers)
        if resp.status_code == 200:
            data = resp.json()
            safe_print(f"Poll {i+1}s: {json.dumps(data)}")
            # Check if there is any indication that the file is processed
            # We will print the keys and check status
            status = data.get("status")
            url = data.get("url")
            safe_print(f" -> status: {status}, url: {url}")
            if status == "processed" or (url is not None and url != ""):
                safe_print(f"[SUCCESS] File processing completed after {i+1} seconds!")
                break
        else:
            safe_print(f"Poll {i+1}s failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    main()
