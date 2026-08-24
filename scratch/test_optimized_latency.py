import time
import requests

print("="*60)
print("  LIVE OPTIMIZATION BENCHMARK TEST")
print("="*60)

# Test 1: /api/profiles
t0 = time.time()
r1 = requests.get("http://127.0.0.1:8080/api/profiles")
t1 = time.time()
d1 = r1.json()
print(f"1. /api/profiles (initial):        {t1-t0:.4f}s | HTTP {r1.status_code} | {len(d1)} bots")

# Test 2: /api/fleet/summary
t0 = time.time()
r2 = requests.get("http://127.0.0.1:8080/api/fleet/summary")
t1 = time.time()
d2 = r2.json()
s2 = d2.get("summary", {})
print(f"2. /api/fleet/summary:             {t1-t0:.4f}s | HTTP {r2.status_code} | {s2.get('total_communities')} comms ({s2.get('total_start_communities')} start)")

# Test 3: /api/fleet/summary?refresh=true
t0 = time.time()
r3 = requests.get("http://127.0.0.1:8080/api/fleet/summary?refresh=true")
t1 = time.time()
d3 = r3.json()
s3 = d3.get("summary", {})
print(f"3. /api/fleet/summary?refresh=true: {t1-t0:.4f}s | HTTP {r3.status_code} | {s3.get('total_communities')} comms")

# Test 4: /api/profiles (subsequent call)
t0 = time.time()
r4 = requests.get("http://127.0.0.1:8080/api/profiles")
t1 = time.time()
print(f"4. /api/profiles (cached):         {t1-t0:.4f}s | HTTP {r4.status_code} | {len(r4.json())} bots")

print("="*60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*60)
