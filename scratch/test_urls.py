import sys
sys.path.append('execution')
from dashboard_server import app

with app.test_client() as client:
    res = client.get('/api/profiles')
    data = res.get_json()
    seen = set()
    for item in data:
        for c in item.get('companies', []):
            name = c.get('company_name')
            url = c.get('whop_url')
            if name not in seen:
                seen.add(name)
                print(f"{name:<22} -> Whop URL: {url}")
