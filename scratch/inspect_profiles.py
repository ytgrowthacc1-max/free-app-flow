import sqlite3
import os
from pathlib import Path

db_paths = [
    Path("profiles.db"),
    Path("c:/Python/Browsing Skill Agent/profiles.db")
]

for db in db_paths:
    if db.exists():
        print(f"=== Database: {db} ===")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            print(f"Tables: {tables}")
            if "profiles" in tables:
                cursor.execute("SELECT * FROM profiles")
                colnames = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                print(f"Columns: {colnames}")
                for r in rows:
                    row_dict = dict(zip(colnames, r))
                    # Print relevant fields
                    print(f"- Profile ID: {row_dict.get('id')} | Email: {row_dict.get('email')} | Platform: {row_dict.get('platform')} | Name/Notes: {row_dict.get('notes') or row_dict.get('name')}")
        except Exception as e:
            print(f"Error reading {db}: {e}")
        finally:
            conn.close()
    else:
        print(f"Database {db} does not exist")
