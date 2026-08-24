import sqlite3
import json

db_path = r"c:\Python\Health_APP_WHOP\prisma\dev.db"

def inspect():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables:", tables)
    
    # Search for Francis/Fit in User
    print("\n--- Users matching 'Francis' or 'Fit' ---")
    cursor.execute("SELECT id, name, email, role FROM User WHERE name LIKE '%Francis%' OR name LIKE '%Fit%' OR email LIKE '%Francis%' OR email LIKE '%Fit%'")
    print(cursor.fetchall())
    
    # Search for Francis/Fit in TrainingProgram
    print("\n--- TrainingPrograms matching 'Francis' or 'Fit' ---")
    cursor.execute("SELECT id, name FROM TrainingProgram WHERE name LIKE '%Francis%' OR name LIKE '%Fit%'")
    print(cursor.fetchall())
    
    # Count of records per table
    print("\n--- Record counts ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        print(f"{table}: {cursor.fetchone()[0]}")
        
    conn.close()

if __name__ == "__main__":
    inspect()
