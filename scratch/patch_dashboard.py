import sys

with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports check
if "from run_campaign_outreach import" not in content:
    import_stmt = "from run_campaign_outreach import execute_campaign, load_campaigns, save_campaigns, get_campaign_by_id\n"
    content = content.replace("from whop_auth import get_fresh_token, is_token_expired", f"from whop_auth import get_fresh_token, is_token_expired\n{import_stmt}")

# 2. Add Nav Tab Button
target_tab_btn = '<button class="tab-btn" id="tab-ignored" onclick="switchFilter(\'ignored\')">'
new_tab_btn = '''<button class="tab-btn" id="tab-campaigns" onclick="switchFilter('campaigns')">
                    📢 Campaigns <span class="tab-badge" id="badge-campaigns" style="background-color: var(--accent-primary);">2</span>
                </button>
                <button class="tab-btn" id="tab-ignored" onclick="switchFilter('ignored')">'''

if "tab-campaigns" not in content:
    content = content.replace(target_tab_btn, new_tab_btn)

# 3. Add API Endpoints
target_api = '@app.route("/api/generate_reply", methods=["POST"])'

new_endpoints = '''@app.route("/api/campaigns", methods=["GET"])
def api_get_campaigns():
    cdata = load_campaigns()
    return jsonify(cdata)

@app.route("/api/campaigns/save", methods=["POST"])
def api_save_campaign():
    req_data = request.json or {}
    cdata = load_campaigns()
    campaigns = cdata.get("campaigns", [])
    
    cid = req_data.get("id")
    if not cid:
        import uuid
        cid = f"campaign_{uuid.uuid4().hex[:8]}"
        req_data["id"] = cid

    found = False
    for i, c in enumerate(campaigns):
        if c.get("id") == cid:
            campaigns[i] = req_data
            found = True
            break
    if not found:
        campaigns.append(req_data)

    cdata["campaigns"] = campaigns
    cdata["active_campaign_id"] = cid
    save_campaigns(cdata)
    return jsonify({"success": True, "campaign": req_data, "campaigns": campaigns})

@app.route("/api/campaigns/delete", methods=["POST"])
def api_delete_campaign():
    req_data = request.json or {}
    cid = req_data.get("id")
    if not cid:
        return jsonify({"error": "Campaign ID required"}), 400

    cdata = load_campaigns()
    campaigns = [c for c in cdata.get("campaigns", []) if c.get("id") != cid]
    cdata["campaigns"] = campaigns
    save_campaigns(cdata)
    return jsonify({"success": True, "campaigns": campaigns})

@app.route("/api/campaigns/run", methods=["POST"])
def api_run_campaign():
    req_data = request.json or {}
    cid = req_data.get("id")
    send_live = req_data.get("send", False)
    limit = req_data.get("limit")
    
    if not cid:
        return jsonify({"error": "Campaign ID required"}), 400

    def _run_task():
        execute_campaign(cid, send=send_live, limit=limit)

    t = threading.Thread(target=_run_task, daemon=True)
    t.start()
    return jsonify({"success": True, "message": f"Campaign '{cid}' started! Mode: {'LIVE' if send_live else 'DRY RUN'}"})

@app.route("/api/generate_reply", methods=["POST"])'''

if "api_get_campaigns" not in content:
    content = content.replace(target_api, new_endpoints)

with open("execution/dashboard_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Patched execution/dashboard_server.py with campaign imports, tab button, and API routes.")
