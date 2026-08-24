import time
import requests

# Trigger live campaign run via dashboard endpoint
res = requests.post("http://localhost:8085/api/campaigns/run", json={"id": "pick_city_promo", "send": True, "limit": 1})
print("Run trigger response:", res.json())

# Poll status for 10 seconds
for i in range(10):
    time.sleep(1)
    st = requests.get("http://localhost:8085/api/campaigns/status").json()
    print(f"\n--- Poll {i+1} --- Status: {st.get('status')} | Success: {st.get('successful')} | Failed: {st.get('failed')}")
    if st.get('logs'):
        print("Last log line:", st['logs'][-1])
    if st.get('status') == 'complete':
        break
