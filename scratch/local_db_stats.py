import sqlite3

conn = sqlite3.connect("c:/Python/Health_APP_WHOP/prisma/dev.db")
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    if table.startswith("_"):
        continue
    cursor.execute(f"SELECT count(*) FROM {table};")
    count = cursor.fetchone()[0]
    print(f"Table: {table} | Local Count: {count}")

conn.close()
