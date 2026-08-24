import os
import sys
import json
from dotenv import load_dotenv

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
    headers = ws.row_values(1)
    print(f"[SUCCESS] Connected! Headers: {headers}")
    
    records = ws.get_all_records()
    print(f"Total Rows: {len(records)}")
    if records:
        print(f"Sample Record 1: {json.dumps(records[0], indent=2)}")
except Exception as e:
    print(f"[ERROR] {e}")
