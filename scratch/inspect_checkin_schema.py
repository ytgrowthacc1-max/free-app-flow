import sqlite3

conn = sqlite3.connect("c:/Python/Health_APP_WHOP/prisma/dev.db")
cursor = conn.cursor()

for t in ["DailyCheckin", "WeightLog"]:
    cursor.execute(f"PRAGMA table_info({t});")
    print(f"Table: {t}")
    for col in cursor.fetchall():
        print(f"  Column: {col[1]} ({col[2]})")

conn.close()
