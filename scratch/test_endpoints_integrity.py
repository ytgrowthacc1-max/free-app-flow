import requests

BASE = "http://127.0.0.1:8080"
endpoints = [
    ("/api/profiles", 200),
    ("/api/fleet/summary", 200),
    ("/api/fleet/summary?refresh=true", 200),
    ("/api/pending", 200),
    ("/api/history", 200),
    ("/api/blacklist", 200),
    ("/api/scheduler_settings", 200),
    ("/api/profile_info", 200),
    ("/api/content_pool", 200),
]

all_passed = True
print("="*60)
print("  API INTEGRITY & FUNCTIONALITY VERIFICATION")
print("="*60)
for ep, expected_code in endpoints:
    try:
        r = requests.get(f"{BASE}{ep}", timeout=5)
        passed = (r.status_code == expected_code)
        status_str = "PASS" if passed else f"FAIL (HTTP {r.status_code})"
        print(f"[{status_str}] GET {ep} -> {r.status_code}")
        if not passed:
            all_passed = False
    except Exception as e:
        print(f"[FAIL] GET {ep} -> Exception: {e}")
        all_passed = False

print("="*60)
if all_passed:
    print("ALL API ENDPOINTS FUNCTIONING WITH 100% SUCCESS!")
else:
    print("WARNING: Some endpoints reported errors.")
print("="*60)
