import sqlite3

conn = sqlite3.connect("c:/Python/Health_APP_WHOP/prisma/dev.db")
cursor = conn.cursor()

cursor.execute("SELECT id, email, name, role FROM User WHERE email='fitfrancis@yahoo.com' OR name LIKE '%Francis%' OR name LIKE '%francis%';")
res = cursor.fetchall()
if res:
    for r in res:
        print(f"Local User found: ID={r[0]}, Email={r[1]}, Name={r[2]}, Role={r[3]}")
else:
    print("No matching local user found.")

conn.close()
