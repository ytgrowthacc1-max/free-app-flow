import requests
import json

# Test pinning bot user_gAkQk98I3AyP4 (donnajacksona7) and community biz_P0QsRCsFSUqpWG
bot_id = "user_gAkQk98I3AyP4"
comp_id = "biz_P0QsRCsFSUqpWG"

print("1. Toggling pin for community...")
r = requests.post("http://localhost:8080/api/toggle_pin", json={"bot_user_id": bot_id, "company_id": comp_id})
print("Response:", r.status_code, r.json())

print("2. Fetching /api/profiles...")
r_prof = requests.get("http://localhost:8080/api/profiles")
profiles = r_prof.json()
donnajackson = next(p for p in profiles if p["bot_user_id"] == bot_id)
print("Donnajackson companies in /api/profiles:", json.dumps(donnajackson["companies"], indent=2))

print("3. Toggling pin back...")
r_back = requests.post("http://localhost:8080/api/toggle_pin", json={"bot_user_id": bot_id, "company_id": comp_id})
print("Response:", r_back.status_code, r_back.json())
