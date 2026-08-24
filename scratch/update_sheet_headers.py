import os
import sys
import json

sys.path.append(r"c:\Python\Browsing Skill Agent\execution")
import gspread
from read_sheet import get_credentials

SPREADSHEET_ID = "14fXyRXAOC9QrkwNYR1AvJ1J8msqlkQYzAX_rhAQjZNA"
TAB_NAME = "USERS_For_messaging"

print(f"Connecting to Google Sheet: {SPREADSHEET_ID}, Tab: {TAB_NAME}...")

try:
    creds = get_credentials()
    client = gspread.authorize(creds)
    sh = client.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(TAB_NAME)
    
    current_headers = ws.row_values(1)
    print(f"Current Headers: {current_headers}")
    
    # Clean and rename headers
    desired_headers = [
        "User Profile Link",   # was 'flex href'
        "Avatar Fallback",    # was 'fui-AvatarFallback'
        "Avatar Image",       # was 'fui-AvatarImage src'
        "Display Name",       # was 'fui-Text'
        "Username",           # was 'fui-Text 2'
        "Source Community",   # was 'Community'
        "Community Niche",    # was 'Community Niche'
        "Contacted?",         # New status column
        "Timestamp",          # New timestamp column
        "Who Contacted?"      # New sender column
    ]
    
    # Update row 1 with new headers
    for idx, h in enumerate(desired_headers, start=1):
        ws.update_cell(1, idx, h)
        
    print(f"[SUCCESS] Updated row 1 headers to: {desired_headers}")
    
    # Fetch distinct source communities to list options
    records = ws.get_all_records()
    source_communities = set()
    for r in records:
        sc = str(r.get("Source Community") or r.get("Community") or "").strip()
        if sc:
            source_communities.add(sc)
            
    print(f"\nDistinct Source Communities in Sheet ({len(source_communities)}):")
    for sc in sorted(list(source_communities))[:20]:
        print(f" - {sc}")

except Exception as e:
    print(f"[ERROR] {e}")
