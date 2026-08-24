import sys
sys.path.append(r"c:\Python\Browsing Skill Agent\execution")
import gspread
from read_sheet import get_credentials

creds = get_credentials()
client = gspread.authorize(creds)
sh = client.open_by_key("14fXyRXAOC9QrkwNYR1AvJ1J8msqlkQYzAX_rhAQjZNA")
ws = sh.worksheet("USERS_For_messaging")
headers = [h.strip() for h in ws.row_values(1)]

col_map = {}
for idx, h in enumerate(headers, start=1):
    lh = h.lower().strip()
    if "who" in lh:
        col_map["who"] = idx
    elif "contacted" in lh:
        col_map["contacted"] = idx
    elif "timestamp" in lh:
        col_map["timestamp"] = idx
    elif "source community" in lh:
        col_map["community"] = idx
    elif "community" in lh and "community" not in col_map:
        col_map["community"] = idx
    elif "username" in lh or "fui-text 2" in lh:
        col_map["username"] = idx
    elif "profile" in lh or "link" in lh or "flex href" in lh:
        col_map["link"] = idx

print("Resolved col_map:", col_map)
for key, col in col_map.items():
    print(f"  Column {col}: '{headers[col-1]}' -> mapped to '{key}'")
