import requests
import urllib.parse

app_id = 'app_8hnbfm1jmFsDa2'
uris = [
    'http://localhost:8000/callback',
    'http://localhost:8000',
    'http://localhost:8000/',
    'http://localhost:8080/callback',
    'http://localhost:8080',
    'http://localhost:3000/callback',
    'http://localhost:3000',
    'http://127.0.0.1:8000/callback',
    'http://127.0.0.1:8080/callback',
    'https://whop.com/callback',
    'http://localhost/callback'
]

print(f"Testing client_id: {app_id}")
for u in uris:
    q = urllib.parse.quote(u, safe="")
    url = f"https://api.whop.com/oauth/authorize?client_id={app_id}&redirect_uri={q}&response_type=code"
    res = requests.get(url)
    print(f"{u} -> status: {res.status_code}, snippet: {res.text[:120]}")
