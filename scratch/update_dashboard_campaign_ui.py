import sys
import os

with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
if "get_campaign_runner_state" not in content:
    content = content.replace(
        "from run_campaign_outreach import execute_campaign, load_campaigns, save_campaigns, get_campaign_by_id",
        "from run_campaign_outreach import execute_campaign, load_campaigns, save_campaigns, get_campaign_by_id, fetch_available_source_communities, get_campaign_runner_state"
    )

# 2. Add API endpoints
target_api = '@app.route("/api/campaigns", methods=["GET"])'

new_api_endpoints = '''@app.route("/api/campaigns/communities", methods=["GET"])
def api_get_campaign_communities():
    communities = fetch_available_source_communities()
    return jsonify({"success": True, "communities": communities})

@app.route("/api/campaigns/status", methods=["GET"])
def api_get_campaign_status():
    st = get_campaign_runner_state()
    return jsonify(st)

@app.route("/api/campaigns", methods=["GET"])'''

if "api_get_campaign_communities" not in content:
    content = content.replace(target_api, new_api_endpoints)

# 3. Replace Source Community Input with Dropdown & Add Live Console Terminal to campaigns-panel
old_source_input = '''                        <div>
                            <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Filter Leads By Source Community</label>
                            <input type="text" id="camp-source-community" class="input-title" value="https://whop.com/joined/profitbets/" placeholder="e.g. https://whop.com/joined/profitbets/" style="margin-top:4px;">
                        </div>'''

new_source_select = '''                        <div>
                            <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Filter Leads By Source Community</label>
                            <select id="camp-source-community" class="input-title" style="margin-top:4px;">
                                <option value="https://whop.com/joined/profitbets/">https://whop.com/joined/profitbets/</option>
                            </select>
                        </div>'''

if old_source_input in content:
    content = content.replace(old_source_input, new_source_select)

# Add Live Console HTML to campaign panel
old_panel_end = '''                    <div style="display:flex; justify-content:flex-end; gap:12px; border-top:1px solid var(--border-color); padding-top:1rem;">
                        <button onclick="runCampaignUI(false)" style="padding:10px 20px; background:rgba(255,255,255,0.06); border:1px solid var(--border-color); border-radius:8px; color:var(--text-main); font-weight:600; cursor:pointer;">⚡ Test Simulation (Dry Run)</button>
                        <button onclick="runCampaignUI(true)" style="padding:10px 24px; background:linear-gradient(135deg,#10b981,#059669); border:none; border-radius:8px; color:white; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(16,185,129,0.3);">🚀 Launch Live Campaign</button>
                    </div>
                </div>
            </div>
        </div>'''

new_panel_end = '''                    <div style="display:flex; justify-content:flex-end; gap:12px; border-top:1px solid var(--border-color); padding-top:1rem;">
                        <button onclick="runCampaignUI(false)" style="padding:10px 20px; background:rgba(255,255,255,0.06); border:1px solid var(--border-color); border-radius:8px; color:var(--text-main); font-weight:600; cursor:pointer;">⚡ Test Simulation (Dry Run)</button>
                        <button onclick="runCampaignUI(true)" style="padding:10px 24px; background:linear-gradient(135deg,#10b981,#059669); border:none; border-radius:8px; color:white; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(16,185,129,0.3);">🚀 Launch Live Campaign</button>
                    </div>

                    <!-- LIVE CAMPAIGN EXECUTION TERMINAL & PROGRESS -->
                    <div style="margin-top:1rem; background:#0e0f17; border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:1.25rem; display:flex; flex-direction:column; gap:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span style="font-size:0.85rem; font-weight:700; color:var(--text-main); text-transform:uppercase; letter-spacing:0.5px;">🖥️ Campaign Execution Console</span>
                                <span id="camp-status-badge" style="font-size:0.7rem; padding:3px 10px; border-radius:12px; background:rgba(255,255,255,0.1); color:var(--text-muted); font-weight:700;">IDLE</span>
                            </div>
                            <div style="font-size:0.78rem; color:var(--text-muted);" id="camp-progress-text">Progress: 0 / 0 (0%)</div>
                        </div>

                        <!-- Progress Bar -->
                        <div style="width:100%; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden;">
                            <div id="camp-progress-bar" style="width:0%; height:100%; background:linear-gradient(90deg, #6366f1, #10b981); transition:width 0.3s ease;"></div>
                        </div>

                        <!-- Console Output Box -->
                        <pre id="camp-log-console" style="background:#07080c; color:#34d399; font-family:'Courier New', monospace; padding:12px; border-radius:8px; height:180px; overflow-y:auto; font-size:0.75rem; border:1px solid rgba(255,255,255,0.06); margin:0; white-space:pre-wrap; word-break:break-word;">Console waiting for campaign launch...</pre>
                    </div>

                </div>
            </div>
        </div>'''

if old_panel_end in content:
    content = content.replace(old_panel_end, new_panel_end)

# 4. JS Functions for Communities Dropdown & Live Polling Console
old_js_fetch = "async function fetchCampaigns() {"

new_js_fetch = '''let campaignPollInterval = null;

async function fetchCommunitiesDropdown() {
    try {
        const res = await fetch('/api/campaigns/communities');
        const data = await res.json();
        const select = document.getElementById('camp-source-community');
        if (select && data.communities) {
            select.innerHTML = '';
            data.communities.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                select.appendChild(opt);
            });
        }
    } catch(e) {
        console.error("Error loading source communities:", e);
    }
}

function startPollingCampaignStatus() {
    if (campaignPollInterval) clearInterval(campaignPollInterval);
    
    const consoleBox = document.getElementById('camp-log-console');
    const badge = document.getElementById('camp-status-badge');
    const pBar = document.getElementById('camp-progress-bar');
    const pText = document.getElementById('camp-progress-text');
    
    campaignPollInterval = setInterval(async () => {
        try {
            const res = await fetch('/api/campaigns/status');
            const data = await res.json();
            
            if (badge) {
                badge.textContent = (data.status || 'IDLE').toUpperCase();
                if (data.status === 'running') {
                    badge.style.background = 'rgba(16,185,129,0.2)';
                    badge.style.color = '#34d399';
                } else if (data.status === 'complete') {
                    badge.style.background = 'rgba(99,102,241,0.2)';
                    badge.style.color = '#a5b4fc';
                } else {
                    badge.style.background = 'rgba(255,255,255,0.1)';
                    badge.style.color = 'var(--text-muted)';
                }
            }

            const total = data.total || 0;
            const processed = data.processed || 0;
            const pct = total > 0 ? Math.round((processed / total) * 100) : 0;

            if (pBar) pBar.style.width = pct + '%';
            if (pText) pText.textContent = `Progress: ${processed} / ${total} (${pct}%) - Success: ${data.successful || 0}, Failed: ${data.failed || 0}`;

            if (consoleBox && data.logs) {
                consoleBox.textContent = data.logs.join('\\n');
                consoleBox.scrollTop = consoleBox.scrollHeight;
            }

            if (data.status === 'complete' || data.status === 'idle') {
                // Keep completed state, stop polling after a bit
                setTimeout(() => { clearInterval(campaignPollInterval); }, 5000);
            }
        } catch(e) {
            console.error("Poll status error:", e);
        }
    }, 1000);
}

async function fetchCampaigns() {
    fetchCommunitiesDropdown();
    startPollingCampaignStatus();'''

if old_js_fetch in content:
    content = content.replace(old_js_fetch, new_js_fetch)

# Update runCampaignUI to start polling instantly
old_run_ui = "alert(`🎉 ${data.message}`);"
new_run_ui = "startPollingCampaignStatus();"

if old_run_ui in content:
    content = content.replace(old_run_ui, new_run_ui)

with open("execution/dashboard_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Applied live console terminal, status polling, and source community dropdown to dashboard_server.py.")
