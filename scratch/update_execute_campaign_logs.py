import sys
import os

with open("execution/run_campaign_outreach.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace execute_campaign function implementation with state-aware version
old_fn_start = "def execute_campaign(campaign_id, send=False, limit=None, progress_callback=None):"

new_fn_code = '''def execute_campaign(campaign_id, send=False, limit=None, progress_callback=None):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        err = f"Campaign '{campaign_id}' not found in configuration."
        add_campaign_log(f"[ERROR] {err}")
        return {"success": False, "error": err, "processed": 0}

    company_id = campaign.get("company_id")
    sender_agent_id = campaign.get("sender_agent_id")
    template = campaign.get("message_template", "")
    delay = campaign.get("delay_seconds", 4)
    target_source = campaign.get("target_source", "google_sheet")
    target_source_community = campaign.get("target_source_community", "https://whop.com/joined/profitbets/")
    target_slug = parse_slug(target_source_community)

    api_key = os.getenv("WHOP_API_KEY")
    if not api_key:
        err = "WHOP_API_KEY is not set in environment."
        add_campaign_log(f"[ERROR] {err}")
        return {"success": False, "error": err, "processed": 0}

    with STATE_LOCK:
        CAMPAIGN_RUNNER_STATE["status"] = "running"
        CAMPAIGN_RUNNER_STATE["campaign_id"] = campaign_id
        CAMPAIGN_RUNNER_STATE["campaign_name"] = campaign.get("name", campaign_id)
        CAMPAIGN_RUNNER_STATE["mode"] = "LIVE SEND" if send else "DRY RUN"
        CAMPAIGN_RUNNER_STATE["total"] = 0
        CAMPAIGN_RUNNER_STATE["processed"] = 0
        CAMPAIGN_RUNNER_STATE["successful"] = 0
        CAMPAIGN_RUNNER_STATE["failed"] = 0
        CAMPAIGN_RUNNER_STATE["logs"] = []

    add_campaign_log("=======================================================")
    add_campaign_log(f"🚀 EXECUTING CAMPAIGN: {campaign.get('name')} ({campaign_id})")
    add_campaign_log(f"   Company ID       : {company_id}")
    add_campaign_log(f"   Sender Agent     : {sender_agent_id or 'Default API App'}")
    add_campaign_log(f"   Target Source    : {target_source}")
    add_campaign_log(f"   Target Community : {target_source_community} (slug: '{target_slug}')")
    add_campaign_log(f"   Mode             : {'LIVE SEND' if send else 'DRY RUN (SIMULATION)'}")
    add_campaign_log("=======================================================")

    targets = []
    if target_source == "manual_list":
        for u in campaign.get("manual_users", []):
            targets.append({"user_id": u, "username": u})
            
    elif target_source == "google_sheet":
        sheet_id = campaign.get("google_sheet_id", SPREADSHEET_ID)
        tab_name = campaign.get("tab_name", DEFAULT_TAB_NAME)
        
        try:
            sys.path.append(r"c:\Python\Browsing Skill Agent\execution")
            import gspread
            from read_sheet import get_credentials
            
            creds = get_credentials()
            client = gspread.authorize(creds)
            sh = client.open_by_key(sheet_id)
            ws = sh.worksheet(tab_name)
            headers = [h.strip() for h in ws.row_values(1)]
            
            col_map = {}
            for idx, h in enumerate(headers, start=1):
                lh = h.lower()
                if "username" in lh or "fui-text 2" in lh:
                    col_map["username"] = idx
                elif "profile" in lh or "link" in lh or "flex href" in lh:
                    col_map["link"] = idx
                elif "source community" in lh or "community" in lh:
                    col_map["community"] = idx
                elif "contacted" in lh:
                    col_map["contacted"] = idx
                elif "timestamp" in lh:
                    col_map["timestamp"] = idx
                elif "who" in lh:
                    col_map["who"] = idx
            
            records = ws.get_all_records()
            add_campaign_log(f"[INFO] Read {len(records)} total records from sheet '{tab_name}'.")

            for r_idx, r in enumerate(records, start=2):
                source_comm = str(r.get("Source Community") or r.get("Community") or "").strip()
                status = str(r.get("Contacted?", "")).strip().lower()
                
                row_slug = parse_slug(source_comm)
                matches_community = not target_slug or (target_slug in row_slug) or (row_slug in target_slug)
                
                if matches_community and status not in ["success"]:
                    raw_uname = str(r.get("Username") or r.get("fui-Text 2") or "").strip()
                    raw_link = str(r.get("User Profile Link") or r.get("flex href") or "").strip()
                    
                    user_target = raw_uname.lstrip('@') or parse_slug(raw_link)
                    if user_target:
                        targets.append({
                            "user_id": user_target,
                            "username": user_target,
                            "display_name": str(r.get("Display Name") or r.get("fui-Text") or user_target),
                            "source_community": source_comm,
                            "row_num": r_idx,
                            "worksheet": ws,
                            "col_map": col_map
                        })
        except Exception as e:
            add_campaign_log(f"[WARNING] Could not read Google Sheet tab '{DEFAULT_TAB_NAME}': {e}. Falling back to manual users.")
            for u in campaign.get("manual_users", []):
                targets.append({"user_id": u, "username": u})

    if limit and len(targets) > limit:
        targets = targets[:limit]

    with STATE_LOCK:
        CAMPAIGN_RUNNER_STATE["total"] = len(targets)

    add_campaign_log(f"[INFO] Total matching target users for '{target_slug}': {len(targets)}")
    if not targets:
        add_campaign_log("[INFO] No pending targets found matching community filter.")
        with STATE_LOCK:
            CAMPAIGN_RUNNER_STATE["status"] = "complete"
        return {"success": True, "processed": 0, "successful": 0, "failed": 0}

    successful = 0
    failed = 0
    results = []

    for idx, target in enumerate(targets):
        uid = target.get("user_id")
        uname = target.get("username", uid)
        disp_name = target.get("display_name", uname)
        
        with STATE_LOCK:
            CAMPAIGN_RUNNER_STATE["processed"] = idx + 1
            CAMPAIGN_RUNNER_STATE["current_target"] = f"@{uname}"
        
        msg_content = template.replace("{{username}}", uname).replace("{{display_name}}", disp_name).replace("{{user_id}}", uid).replace("{{company_name}}", campaign.get("company_name", ""))
        
        add_campaign_log(f"[{idx+1}/{len(targets)}] Processing @{uname} (ID: {uid})...")
        add_campaign_log(f"   Preview: \"{msg_content[:70]}...\"")

        if not send:
            add_campaign_log(f"   ⚡ [DRY RUN] Simulated message dispatch to @{uname}.")
            successful += 1
            with STATE_LOCK:
                CAMPAIGN_RUNNER_STATE["successful"] = successful
            results.append({"target": uid, "status": "simulated", "channel_id": "sim_feed_123"})
            if progress_callback:
                progress_callback(idx + 1, len(targets), uid, "simulated")
            continue

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if sender_agent_id:
            headers["X-On-Behalf-Of"] = sender_agent_id

        url_chan = "https://api.whop.com/api/v1/support_channels"
        payload_chan = {"company_id": company_id, "user_id": uid}
        
        try:
            res_c = requests.post(url_chan, headers=headers, json=payload_chan, timeout=10)
            if res_c.status_code not in [200, 201]:
                add_campaign_log(f"   ❌ [FAILED] Support channel creation HTTP {res_c.status_code}: {res_c.text}")
                failed += 1
                with STATE_LOCK:
                    CAMPAIGN_RUNNER_STATE["failed"] = failed
                results.append({"target": uid, "status": "failed", "error": res_c.text})
                continue

            chan_id = res_c.json().get("id")
            
            url_msg = "https://api.whop.com/api/v1/messages"
            payload_msg = {"channel_id": chan_id, "content": msg_content}
            res_m = requests.post(url_msg, headers=headers, json=payload_msg, timeout=10)
            
            if res_m.status_code in [200, 201]:
                mdata = res_m.json()
                msg_id = mdata.get("id")
                sender_info = mdata.get("user", {})
                sender_name = f"@{sender_info.get('username')}" if sender_info.get('username') else (campaign.get("sender_agent_username") or "supportpickcity")
                add_campaign_log(f"   ✅ [SUCCESS] Delivered to @{uname}! (Msg ID: {msg_id}) Sent as {sender_name}")
                successful += 1
                with STATE_LOCK:
                    CAMPAIGN_RUNNER_STATE["successful"] = successful
                results.append({
                    "target": uid,
                    "status": "success",
                    "channel_id": chan_id,
                    "message_id": msg_id,
                    "sender": sender_name
                })
                
                ws = target.get("worksheet")
                row_num = target.get("row_num")
                col_map = target.get("col_map", {})
                if ws and row_num:
                    try:
                        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if col_map.get("contacted"):
                            ws.update_cell(row_num, col_map["contacted"], "Success")
                        if col_map.get("timestamp"):
                            ws.update_cell(row_num, col_map["timestamp"], ts)
                        if col_map.get("who"):
                            ws.update_cell(row_num, col_map["who"], sender_name)
                    except Exception as e_sheet:
                        add_campaign_log(f"   [WARN] Sheet update error on row {row_num}: {e_sheet}")
            else:
                add_campaign_log(f"   ❌ [FAILED] Message send HTTP {res_m.status_code}: {res_m.text}")
                failed += 1
                with STATE_LOCK:
                    CAMPAIGN_RUNNER_STATE["failed"] = failed
                results.append({"target": uid, "status": "failed", "error": res_m.text})

        except Exception as ex:
            add_campaign_log(f"   ❌ [ERROR] Exception processing {uid}: {ex}")
            failed += 1
            with STATE_LOCK:
                CAMPAIGN_RUNNER_STATE["failed"] = failed
            results.append({"target": uid, "status": "error", "error": str(ex)})

        log_campaign_result(campaign_id, {
            "target": uid,
            "success": (results[-1]["status"] == "success"),
            "details": results[-1]
        })

        if progress_callback:
            progress_callback(idx + 1, len(targets), uid, results[-1]["status"])

        if idx < len(targets) - 1:
            time.sleep(delay)

    add_campaign_log("=======================================================")
    add_campaign_log(f"🎉 CAMPAIGN COMPLETE: {campaign.get('name')}")
    add_campaign_log(f"   Successful: {successful}")
    add_campaign_log(f"   Failed    : {failed}")
    add_campaign_log("=======================================================")

    with STATE_LOCK:
        CAMPAIGN_RUNNER_STATE["status"] = "complete"

    return {
        "success": True,
        "processed": len(targets),
        "successful": successful,
        "failed": failed,
        "results": results
    }
'''

# Find execute_campaign block in run_campaign_outreach.py and replace
if old_fn_start in content:
    fn_end_idx = content.find("def main():")
    content = content[:content.find(old_fn_start)] + new_fn_code + "\n\n" + content[fn_end_idx:]

with open("execution/run_campaign_outreach.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Replaced execute_campaign with live state-aware version.")
