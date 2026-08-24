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

SHEET_ID = "14fXyRXAOC9QrkwNYR1AvJ1J8msqlkQYzAX_rhAQjZNA"
FITNESS_LEADS_PATH = r"c:\Python\WHOP AUTOMATION AGENTIC\fitness_leads.json"
DEFAULT_OPENER = "hey were you the one i was sorting out that free custom app build for? just gotta lock the hosting and we good"

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

    log.info(f"Loaded {len(records)} existing rows from Google Sheet.")
    
    existing_links = set()
    for r in records:
        link = r.get("community link", "").strip().lower()
        if link:
            existing_links.add(link)

    # 2. Check local fitness_leads.json
    if not os.path.exists(FITNESS_LEADS_PATH):
        log.error(f"fitness_leads.json not found at {FITNESS_LEADS_PATH}")
        sys.exit(1)

    log.info("Loading fitness_leads.json...")
    with open(FITNESS_LEADS_PATH, "r", encoding="utf-8") as f:
        all_leads = json.load(f)

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

    log.info(f"Found {len(qualified_leads)} total qualified fitness leads.")
    
    # 3. Filter duplicates
    new_qualified = []
    for l in qualified_leads:
        if l["link"].strip().lower() in existing_links:
            continue
        new_qualified.append(l)

    log.info(f"Found {len(new_qualified)} new qualified fitness leads NOT currently in the sheet.")
    
    # 4. Limit to exactly 50
    to_add = new_qualified[:50]
    if not to_add:
        log.info("No new unique leads to add.")
        return

    log.info(f"Adding exactly {len(to_add)} leads to the Google Sheet...")
    
    rows_to_append = []
    for l in to_add:
        # Schema: community link, opener, Contacted?, Who contacted?, Timestamp, name, reviews, members, socials, description
        rows_to_append.append([
            l["link"],
            DEFAULT_OPENER,
            "",  # Contacted?
            "",  # Who contacted?
            "",  # Timestamp
            l["name"],
            l.get("reviews", 0),
            l.get("members", 0),
            l.get("socials", ""),
            l.get("description", "")[:500]  # Limit length for readability
        ])

    try:
        ws.append_rows(rows_to_append)
        log.info(f"Successfully appended {len(to_add)} leads to Google Sheets.")
    except Exception as e:
        log.error(f"Failed to append rows to sheet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
