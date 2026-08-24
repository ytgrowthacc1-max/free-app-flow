import sqlite3

db_path = r"c:\Python\Browsing Skill Agent\profiles.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT account_number, name, whop_username, whop_name, status FROM profiles WHERE whop_username LIKE '%marie%' OR whop_username LIKE '%app%' OR name LIKE '%marie%' OR name LIKE '%app%';")
rows = cursor.fetchall()
print(f"Found {len(rows)} matching profiles:")
for r in rows:
    print(r)

print("\nListing all profiles with whop_username set:")
cursor.execute("SELECT account_number, name, whop_username, whop_name, status FROM profiles WHERE whop_username IS NOT NULL AND whop_username != '';")
rows = cursor.fetchall()
for r in rows:
    print(r)

conn.close()
