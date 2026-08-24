import subprocess
import time
import requests
import json

def main():
    print("[INFO] Starting ngrok on port 8090...")
    # Start ngrok in background without blocking
    try:
        proc = subprocess.Popen(["ngrok", "http", "8090"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print("[ERROR] Failed to start ngrok process:", e)
        return
        
    # Wait for ngrok to initialize and create the tunnel
    time.sleep(3)
    
    # Query local ngrok API to find the public URL
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tunnels = data.get("tunnels", [])
            https_url = None
            for t in tunnels:
                if t.get("proto") == "https":
                    https_url = t.get("public_url")
                    break
            
            if not https_url and tunnels:
                https_url = tunnels[0].get("public_url")
                
            if https_url:
                print("\n" + "="*70)
                print(f" SUCCESS: ngrok tunnel is active!")
                print(f" Public URL: {https_url}")
                print(f" Please set this URL as your Whop App URL.")
                print("="*70 + "\n")
                
                # Save URL to a temp file so we can query or reference it
                with open(".tmp/ngrok_url.txt", "w", encoding="utf-8") as f:
                    f.write(https_url)
            else:
                print("[ERROR] No active tunnels found in ngrok API response:", data)
        else:
            print("[ERROR] Failed to query ngrok API. Status:", resp.status_code)
    except Exception as e:
        print("[ERROR] Could not connect to ngrok local API. Make sure ngrok is running:", e)

if __name__ == "__main__":
    main()
