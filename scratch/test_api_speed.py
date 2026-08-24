import requests
import time

t0 = time.time()
try:
    r = requests.get("http://localhost:8080/api/actions", timeout=5)
    t1 = time.time()
    print(f"Status: {r.status_code}, Elapsed: {t1-t0:.3f}s")
    data = r.json()
    print(f"Loaded {len(data)} actions from API cleanly.")
except Exception as e:
    print(f"Error: {e}")
