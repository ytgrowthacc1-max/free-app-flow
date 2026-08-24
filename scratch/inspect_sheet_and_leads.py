import os
import sys
import json
import logging

# Ensure UTF-8 printing on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Add Browsing Skill Agent execution directory to path to load read_sheet
sys.path.append(r"c:\Python\Browsing Skill Agent\execution")
sys.path.append(r"c:\Python\WHOP AUTOMATION AGENTIC\execution")

import gspread
from read_sheet import get_credentials
import profile_db as db

SHEET_ID = "14fXyRXAOC9QrkwNYR1AvJ1J8msqlkQYzAX_rhAQjZNA"
FITNESS_LEADS_PATH = r"c:\Python\WHOP AUTOMATION AGENTIC\fitness_leads.json"

FITNESS_KEYWORDS = [
    "fit", "gym", "workout", "coaching", "physique", "body", "nutrition", 
    "diet", "muscle", "health", "wellness", "athlete", "athletic", 
    "run", "train", "sudar", "femboy", "mamacitas", "teambff", "physique"
]

EXCLUDE_KEYWORDS = [
    "trading", "crypto", "pips", "signals", "sportsbook", "betting", 
    "resell", "amazon", "fba", "dropshipping", "money", "profit", 
    "trades", "capital", "forex", "cash", "wealth", "airdrop", "whop-product"
]

def main():
    # 1. Connect to Sheet
    log.info("Connecting to Google Sheet...")
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        sh = client.open_by_key(SHEET_ID)
        ws = sh.worksheet("Main")
        records = ws.get_all_records()
    except Exception as e:
        log.error(f"Failed to access Google Sheet: {e}")
        sys.exit(1)

    log.info(f"Loaded {len(records)} rows from Google Sheet.")
    
    contacted_success = 0
    contacted_failed = 0
    pending = 0
    existing_links = set()

    for r in records:
        link = r.get("community link", "").strip().lower()
        if not link:
            continue
        existing_links.add(link)
        
        status = str(r.get("Contacted?", "")).strip().lower()
        if status == "success":
            contacted_success += 1
        elif status == "failed":
            contacted_failed += 1
        else:
            pending += 1

    log.info(f"Sheet Statistics:")
    log.info(f" - Total Leads: {len(existing_links)}")
    log.info(f" - Contacted Success: {contacted_success}")
    log.info(f" - Contacted Failed: {contacted_failed}")
    log.info(f" - Pending: {pending}")

    # 2. Check local fitness_leads.json
    if not os.path.exists(FITNESS_LEADS_PATH):
        log.error(f"fitness_leads.json not found at {FITNESS_LEADS_PATH}")
        return

    log.info("Loading fitness_leads.json...")
    with open(FITNESS_LEADS_PATH, "r", encoding="utf-8") as f:
        all_leads = json.load(f)

    log.info(f"Found {len(all_leads)} raw leads in JSON.")
    
    qualified_leads = []
    for l in all_leads:
        name = l.get("name", "")
        link = l.get("link", "")
        desc = l.get("description", "")
        
        name_lower = name.lower()
        desc_lower = desc.lower()
        link_lower = link.lower()
        
        # Filter exclusions
        is_excluded = False
        for ex in EXCLUDE_KEYWORDS:
            if ex in name_lower or ex in desc_lower or ex in link_lower:
                is_excluded = True
                break
        if is_excluded:
            continue
            
        # Filter inclusions
        has_fit = False
        for kw in FITNESS_KEYWORDS:
            if kw in name_lower or kw in desc_lower or kw in link_lower:
                has_fit = True
                break
        if not has_fit:
            continue
            
        qualified_leads.append(l)

    log.info(f"Found {len(qualified_leads)} qualified fitness leads after applying keyword filters.")
    
    # 3. Filter duplicates (already in Google Sheet)
    new_qualified = []
    for l in qualified_leads:
        if l["link"].strip().lower() in existing_links:
            continue
        new_qualified.append(l)

    log.info(f"Found {len(new_qualified)} new qualified fitness leads NOT currently in the Google Sheet.")

if __name__ == "__main__":
    main()
