import time
import requests

def main():
    print("[INFO] Polling http://localhost:8080/api/auth_status for authentication success...")
    for _ in range(300): # Poll for up to 5 minutes
        try:
            r = requests.get("http://localhost:8080/api/auth_status", timeout=2)
            if r.status_code == 200:
                data = r.json()
                if data.get("success"):
                    print("[SUCCESS] OAuth callback received and processed by dashboard server!")
                    return
            else:
                print(f"[WARNING] API returned status code {r.status_code}")
        except Exception as e:
            print(f"[WARNING] Request failed: {e}")
        time.sleep(1)
    print("[TIMEOUT] Authorization polling timed out after 5 minutes.")

if __name__ == "__main__":
    main()
