import requests

try:
    r = requests.get("http://127.0.0.1:5000/api/experiences")
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)
except Exception as e:
    print("ERROR calling localhost:5000:", e)
