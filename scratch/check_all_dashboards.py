import requests

dashboards = {
    "Whop Automation Forum Dashboard": "http://localhost:8080/",
    "Whop Outreach Campaign Dashboard": "http://localhost:8085/",
    "Health App Dashboard": "http://localhost:3000/"
}

for name, url in dashboards.items():
    try:
        r = requests.get(url, timeout=3)
        print(f"[ONLINE] {name}: Status {r.status_code} -> {url}")
    except Exception as e:
        print(f"[OFFLINE] {name}: ({e}) -> {url}")
