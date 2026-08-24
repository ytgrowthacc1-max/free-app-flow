import sqlite3

db_path = r"c:\Python\Browsing Skill Agent\profiles.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
schemas = cursor.fetchall()
for schema in schemas:
    print(schema[0])
    print("-" * 50)

conn.close()
