import urllib.request
import base64
import json
import time
import os

creds = base64.b64encode(b"admin:whopautomation").decode()
req = urllib.request.Request("http://127.0.0.1:8080/api/fleet/summary", headers={"Authorization": f"Basic {creds}"})

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    communities = data.get("communities", [])
    now = time.time()
    
    out_lines = []
    out_lines.append(f"Success: {data.get('success')}")
    out_lines.append(f"Total communities in fleet: {len(communities)}")
    out_lines.append("\n--- ACCOUNTS AUDIT (>30m / >48m inactive) ---")
    
    stale_count = 0
    for c in communities:
        bot_user_id = c.get("bot_user_id")
        bot_username = c.get("bot_username")
        company_id = c.get("company_id")
        company_name = c.get("company_name")
        last_active = c.get("last_active_timestamp") or c.get("last_active") or c.get("last_post_timestamp") or 0
        
        minutes_ago = (now - last_active) / 60 if isinstance(last_active, (int, float)) and last_active > 0 else -1
        
        out_lines.append(f"Bot: @{bot_username} ({bot_user_id}) | Community: {company_name} ({company_id})")
        out_lines.append(f"  -> Last Active: {minutes_ago:.1f} mins ago ({last_active})")
        out_lines.append(f"  -> Data: {json.dumps(c, indent=2)}\n")

    report_path = os.path.join(os.path.dirname(__file__), "fleet_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
        
    print(f"Report written to {report_path}. Total communities: {len(communities)}")

except Exception as e:
    print(f"Error fetching fleet summary: {e}")
