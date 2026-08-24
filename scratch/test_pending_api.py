import requests
import time

t0 = time.time()
try:
    r = requests.get("http://localhost:8080/api/pending", timeout=5)
    t1 = time.time()
    print(f"Status: {r.status_code}, Elapsed: {t1-t0:.3f}s")
    data = r.json()
    print(f"Pending items count returned: {len(data)}")
except Exception as e:
    print(f"Error: {e}")
