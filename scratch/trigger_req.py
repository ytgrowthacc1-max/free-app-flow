import urllib.request
import urllib.error

url = "https://14114d70.health-app-whop.pages.dev/api/dashboard"
print("Sending request to:", url)
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        print("Status:", response.status)
        print(response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.reason)
    try:
        print(e.read().decode("utf-8"))
    except:
        pass
except Exception as e:
    print("Error:", e)
