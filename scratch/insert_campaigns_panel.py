import sys

with open("execution/dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Panel Insertion
target_marker = '<div class="workspace-panels" id="scheduler-panel"'

panel_html = '''        <div class="workspace-panels" id="campaigns-panel" style="display: none; padding: 2rem 2.5rem; overflow-y: auto; flex-direction: column; gap: 1.5rem; background: var(--workspace-bg); width: 100%; box-sizing: border-box;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color); padding-bottom:1.25rem; flex-shrink:0;">
                <div>
                    <h2 style="font-size:1.35rem; font-weight:600;">📢 Multi-Community Outreach Campaigns</h2>
                    <p style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;">Manage community outreach presets, select sender agents (e.g. @supportpickcity), set copy, and launch batch dispatches.</p>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <button onclick="createNewCampaignUI()" style="padding:8px 16px; background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3); border-radius:8px; color:#a5b4fc; font-size:0.85rem; cursor:pointer; font-weight:600;">➕ New Campaign</button>
                    <button onclick="saveCurrentCampaignUI()" style="padding:8px 18px; background:linear-gradient(135deg,var(--accent-primary),#7c3aed); border:none; border-radius:8px; color:white; font-size:0.85rem; cursor:pointer; font-weight:600;">💾 Save Preset</button>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 320px 1fr; gap: 1.5rem; width: 100%;">
                <div style="background:var(--card-bg); border:1px solid var(--border-color); border-radius:12px; padding:1.25rem; display:flex; flex-direction:column; gap:1rem;">
                    <h3 style="font-size:0.85rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.8px;">Saved Campaigns</h3>
                    <div id="campaigns-preset-list" style="display:flex; flex-direction:column; gap:8px;">
                    </div>
                </div>

                <div style="background:var(--card-bg); border:1px solid var(--border-color); border-radius:12px; padding:1.5rem; display:flex; flex-direction:column; gap:1.25rem;">
                    <input type="hidden" id="camp-id" value="pick_city_promo">
                    
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
                        <div>
                            <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Campaign Title</label>
                            <input type="text" id="camp-name" class="input-title" value="Pick City | 5.0 Star Review Promo" style="margin-top:4px;">
                        </div>
                        <div>
                            <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Target Community (Company ID)</label>
                            <input type="text" id="camp-company-id" class="input-title" value="biz_78VckYvrZN8g34" style="margin-top:4px;">
                        </div>
                    </div>

                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
                        <div>
                            <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Sender Agent User ID (X-On-Behalf-Of)</label>
                            <select id="camp-sender-agent" class="input-title" style="margin-top:4px;">
                                <option value="user_X1Uk8voCxS7Vs">@supportpickcity (user_X1Uk8voCxS7Vs)</option>
                                <option value="user_JPHEqzhggecW9">@sidneysanders61 (user_JPHEqzhggecW9)</option>
                                <option value="">Default API Key identity</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Target Recipient Source</label>
                            <select id="camp-target-source" class="input-title" style="margin-top:4px;">
                                <option value="manual_list">Manual User List / Test Users</option>
                                <option value="google_sheet">Google Sheet (Main Tab)</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Manual Recipient User IDs / Slugs (Comma Separated)</label>
                        <input type="text" id="camp-manual-users" class="input-title" value="user_fdWsHxrBCGa62" style="margin-top:4px;">
                    </div>

                    <div>
                        <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Promotional Copy / Message Template</label>
                        <textarea id="camp-message-template" class="textarea-response" style="margin-top:4px; min-height:160px;"></textarea>
                    </div>

                    <div style="display:flex; justify-content:flex-end; gap:12px; border-top:1px solid var(--border-color); padding-top:1rem;">
                        <button onclick="runCampaignUI(false)" style="padding:10px 20px; background:rgba(255,255,255,0.06); border:1px solid var(--border-color); border-radius:8px; color:var(--text-main); font-weight:600; cursor:pointer;">⚡ Test Simulation (Dry Run)</button>
                        <button onclick="runCampaignUI(true)" style="padding:10px 24px; background:linear-gradient(135deg,#10b981,#059669); border:none; border-radius:8px; color:white; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(16,185,129,0.3);">🚀 Launch Live Campaign</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="workspace-panels" id="scheduler-panel"'''

if "id=\"campaigns-panel\"" not in content:
    content = content.replace(target_marker, panel_html)

# 2. Add JS logic for Campaign Manager
js_code = '''
let currentCampaigns = [];

async function fetchCampaigns() {
    try {
        const res = await fetch('/api/campaigns');
        const data = await res.json();
        currentCampaigns = data.campaigns || [];
        renderCampaignPresetsList();
        if (currentCampaigns.length > 0) {
            selectCampaignPreset(currentCampaigns[0].id);
        }
    } catch(e) {
        console.error("Error fetching campaigns:", e);
    }
}

function renderCampaignPresetsList() {
    const container = document.getElementById('campaigns-preset-list');
    if (!container) return;
    container.innerHTML = '';
    
    currentCampaigns.forEach(c => {
        const div = document.createElement('div');
        div.className = 'list-item';
        div.onclick = () => selectCampaignPreset(c.id);
        div.innerHTML = `
            <div style="font-size:0.85rem; font-weight:700; color:var(--text-main);">${c.name}</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Agent: @${c.sender_agent_username || 'default'}</div>
            <div style="font-size:0.68rem; color:#a5b4fc; margin-top:2px;">Community: ${c.company_id}</div>
        `;
        container.appendChild(div);
    });
}

function selectCampaignPreset(id) {
    const c = currentCampaigns.find(x => x.id === id);
    if (!c) return;
    document.getElementById('camp-id').value = c.id;
    document.getElementById('camp-name').value = c.name || '';
    document.getElementById('camp-company-id').value = c.company_id || '';
    document.getElementById('camp-sender-agent').value = c.sender_agent_id || '';
    document.getElementById('camp-target-source').value = c.target_source || 'manual_list';
    document.getElementById('camp-manual-users').value = (c.manual_users || []).join(', ');
    document.getElementById('camp-message-template').value = c.message_template || '';
}

function createNewCampaignUI() {
    const newId = 'campaign_' + Math.random().toString(36).substring(2, 8);
    document.getElementById('camp-id').value = newId;
    document.getElementById('camp-name').value = 'New Community Campaign';
    document.getElementById('camp-company-id').value = 'biz_78VckYvrZN8g34';
    document.getElementById('camp-sender-agent').value = 'user_X1Uk8voCxS7Vs';
    document.getElementById('camp-target-source').value = 'manual_list';
    document.getElementById('camp-manual-users').value = 'user_fdWsHxrBCGa62';
    document.getElementById('camp-message-template').value = 'Hello! Check out our community here...';
}

async function saveCurrentCampaignUI() {
    const rawManual = document.getElementById('camp-manual-users').value || '';
    const manualUsers = rawManual.split(',').map(x => x.strip ? x.strip() : x.trim()).filter(Boolean);
    const agentSelect = document.getElementById('camp-sender-agent');
    const agentUsername = agentSelect.options[agentSelect.selectedIndex].text.split(' ')[0].replace('@', '');

    const payload = {
        id: document.getElementById('camp-id').value,
        name: document.getElementById('camp-name').value,
        company_id: document.getElementById('camp-company-id').value,
        sender_agent_id: agentSelect.value,
        sender_agent_username: agentUsername,
        target_source: document.getElementById('camp-target-source').value,
        manual_users: manualUsers,
        message_template: document.getElementById('camp-message-template').value,
        delay_seconds: 4
    };

    try {
        const res = await fetch('/api/campaigns/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert('✅ Campaign Preset Saved Successfully!');
            fetchCampaigns();
        }
    } catch(e) {
        alert('Failed to save campaign: ' + e);
    }
}

async function runCampaignUI(sendLive) {
    const id = document.getElementById('camp-id').value;
    const modeStr = sendLive ? "LIVE SENDING" : "DRY RUN SIMULATION";
    if (sendLive && !confirm("🚀 Are you sure you want to launch LIVE SENDING for this campaign?")) {
        return;
    }
    
    try {
        const res = await fetch('/api/campaigns/run', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id: id, send: sendLive })
        });
        const data = await res.json();
        alert(`🎉 ${data.message}`);
    } catch(e) {
        alert('Error triggering campaign: ' + e);
    }
}
'''

if "function fetchCampaigns()" not in content:
    content = content.replace("function switchFilter(filter) {", js_code + "\nfunction switchFilter(filter) {\nif(filter === 'campaigns'){ document.querySelectorAll('.workspace-panels').forEach(p=>p.style.display='none'); document.getElementById('campaigns-panel').style.display='flex'; fetchCampaigns(); return; }\n")

with open("execution/dashboard_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Inserted #campaigns-panel and JS functions into execution/dashboard_server.py")
