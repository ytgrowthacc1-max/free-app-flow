import requests

try:
    r = requests.get('http://localhost:8080/', timeout=5)
    print("Dashboard status code:", r.status_code)
    print("Page title in HTML:", 'Whop Automation Hub' in r.text)
except Exception as e:
    print("Dashboard error:", e)
