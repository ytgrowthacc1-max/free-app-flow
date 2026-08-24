import sqlite3
import subprocess
import json
import os
import sys

# Paths
LOCAL_DB = "c:/Python/Health_APP_WHOP/prisma/dev.db"
WRANGLER_CONFIG = "../Health_APP_WHOP/wrangler.toml"
BACKUP_SQL = "scratch/d1_backup_full.sql"
MIGRATION_SQL = "scratch/deploy_migration.sql"

print("Step 1: Backing up remote D1 database to sql...")
cmd_backup = [
    "npx", "wrangler", "d1", "export", "DB", 
    "--remote", f"--output={BACKUP_SQL}", 
    f"--config={WRANGLER_CONFIG}"
]
res_backup = subprocess.run(cmd_backup, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
if res_backup.returncode != 0:
    print("Backup failed:", res_backup.stderr)
    sys.exit(1)
print("Backup completed successfully! Saved to", BACKUP_SQL)

# Helpers to query remote D1
def query_remote(sql):
    cmd = [
        "npx", "wrangler", "d1", "execute", "DB", 
        "--remote", f"--command={sql}", 
        f"--config={WRANGLER_CONFIG}", "--json"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    if res.returncode != 0:
        raise Exception(f"Query failed: {res.stderr}\nCommand: {sql}")
    try:
        data = json.loads(res.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("results", [])
        return []
    except Exception as e:
        raise Exception(f"JSON parse failed: {e}\nOutput: {res.stdout}")

print("\nStep 2: Fetching Fit Francis related data from remote D1...")

# Preserved IDs
PRESERVED_USER_IDS = ["0ebb68c1-9af5-4560-8aba-593e4b793afe", "9de9fd03-c894-4864-b5a7-72938c4cf64c", "owner-seeyoulaterleaner"]
PRESERVED_PROGRAM_IDS = ["91f4d177-440f-4a2a-9211-20cb46c7e31b", "8a5336b6-ae24-48fe-a94d-fa7a2d9f21f2", "dbd17282-36e0-4f2a-8124-cd7517e97083"]

remote_data = {}

# 1. Users
remote_data["User"] = query_remote(f"SELECT * FROM User WHERE id IN {tuple(PRESERVED_USER_IDS)};")
print(f"  Preserved Users: {len(remote_data['User'])}")

# 2. CoachCustomerAssignment
remote_data["CoachCustomerAssignment"] = query_remote(f"SELECT * FROM CoachCustomerAssignment WHERE customerId IN ('0ebb68c1-9af5-4560-8aba-593e4b793afe', '9de9fd03-c894-4864-b5a7-72938c4cf64c') OR coachId = 'owner-seeyoulaterleaner';")
print(f"  Preserved CoachCustomerAssignments: {len(remote_data['CoachCustomerAssignment'])}")

# 3. TrainingPrograms
remote_data["TrainingProgram"] = query_remote(f"SELECT * FROM TrainingProgram WHERE id IN {tuple(PRESERVED_PROGRAM_IDS)};")
print(f"  Preserved TrainingPrograms: {len(remote_data['TrainingProgram'])}")

# 4. Workouts
remote_data["Workout"] = query_remote(f"SELECT * FROM Workout WHERE trainingProgramId IN {tuple(PRESERVED_PROGRAM_IDS)};")
print(f"  Preserved Workouts: {len(remote_data['Workout'])}")

# 5. WorkoutExercises
workout_ids = [w["id"] for w in remote_data["Workout"]]
if workout_ids:
    workout_ids_str = ", ".join(f"'{wid}'" for wid in workout_ids)
    remote_data["WorkoutExercise"] = query_remote(f"SELECT * FROM WorkoutExercise WHERE workoutId IN ({workout_ids_str});")
else:
    remote_data["WorkoutExercise"] = []
print(f"  Preserved WorkoutExercises: {len(remote_data['WorkoutExercise'])}")

# 6. TrainingAssignments
remote_data["TrainingAssignment"] = query_remote(f"SELECT * FROM TrainingAssignment WHERE trainingProgramId IN {tuple(PRESERVED_PROGRAM_IDS)} OR customerId IN ('0ebb68c1-9af5-4560-8aba-593e4b793afe', '9de9fd03-c894-4864-b5a7-72938c4cf64c');")
print(f"  Preserved TrainingAssignments: {len(remote_data['TrainingAssignment'])}")

# 7. DailyCheckins
remote_data["DailyCheckin"] = query_remote("SELECT * FROM DailyCheckin WHERE customerId IN ('0ebb68c1-9af5-4560-8aba-593e4b793afe', '9de9fd03-c894-4864-b5a7-72938c4cf64c');")
print(f"  Preserved DailyCheckins: {len(remote_data['DailyCheckin'])}")

# 8. WeightLogs
remote_data["WeightLog"] = query_remote("SELECT * FROM WeightLog WHERE customerId IN ('0ebb68c1-9af5-4560-8aba-593e4b793afe', '9de9fd03-c894-4864-b5a7-72938c4cf64c');")
print(f"  Preserved WeightLogs: {len(remote_data['WeightLog'])}")

# 9. NutritionAssignments
remote_data["NutritionAssignment"] = query_remote("SELECT * FROM NutritionAssignment WHERE customerId IN ('0ebb68c1-9af5-4560-8aba-593e4b793afe', '9de9fd03-c894-4864-b5a7-72938c4cf64c');")
print(f"  Preserved NutritionAssignments: {len(remote_data['NutritionAssignment'])}")

# 10. SupplementAssignments
remote_data["SupplementAssignment"] = query_remote("SELECT * FROM SupplementAssignment WHERE customerId IN ('0ebb68c1-9af5-4560-8aba-593e4b793afe', '9de9fd03-c894-4864-b5a7-72938c4cf64c');")
print(f"  Preserved SupplementAssignments: {len(remote_data['SupplementAssignment'])}")

# 11. Exercises referenced by preserved workouts
exercise_ids = list(set([we["exerciseId"] for we in remote_data["WorkoutExercise"]]))
local_conn = sqlite3.connect(LOCAL_DB)
local_cursor = local_conn.cursor()

local_cursor.execute("SELECT id FROM Exercise;")
local_exercise_ids = set([r[0] for r in local_cursor.fetchall()])

missing_exercises = [eid for eid in exercise_ids if eid not in local_exercise_ids]
if missing_exercises:
    missing_exercises_str = ", ".join(f"'{eid}'" for eid in missing_exercises)
    remote_data["Exercise"] = query_remote(f"SELECT * FROM Exercise WHERE id IN ({missing_exercises_str});")
else:
    remote_data["Exercise"] = []
print(f"  Preserved missing Exercises from D1: {len(remote_data['Exercise'])}")

print("\nStep 3: Loading local database records...")
local_data = {}
local_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in local_cursor.fetchall() if not t[0].startswith("_") and t[0] != "sqlite_sequence"]

for table in tables:
    local_cursor.execute(f"SELECT * FROM {table};")
    cols = [d[0] for d in local_cursor.description]
    rows = local_cursor.fetchall()
    local_data[table] = [dict(zip(cols, row)) for row in rows]
    print(f"  Local table {table}: {len(rows)} records")

local_conn.close()

# Cleanup local data to avoid collisions with preserved IDs
print("\nStep 4: Mapping user IDs and deduplicating local records against preserved remote ones...")

USER_ID_MAPPING = {
    "cmjt39bdc0000jo04s4jl7jmt": "owner-seeyoulaterleaner",
    "cmn3po9zq0000ib04bbcma3ge": "0ebb68c1-9af5-4560-8aba-593e4b793afe",
    "9de9fd03-c894-4864-b5a7-72938c4cf64c": "9de9fd03-c894-4864-b5a7-72938c4cf64c"
}

# 1. Map user IDs in local data
mapped_local_data = {}
for table, rows in local_data.items():
    mapped_rows = []
    for row in rows:
        new_row = dict(row)
        # Map ID
        if "id" in new_row and new_row["id"] in USER_ID_MAPPING:
            new_row["id"] = USER_ID_MAPPING[new_row["id"]]
        # Map ownerId
        if "ownerId" in new_row and new_row["ownerId"] in USER_ID_MAPPING:
            new_row["ownerId"] = USER_ID_MAPPING[new_row["ownerId"]]
        # Map customerId
        if "customerId" in new_row and new_row["customerId"] in USER_ID_MAPPING:
            new_row["customerId"] = USER_ID_MAPPING[new_row["customerId"]]
        # Map coachId
        if "coachId" in new_row and new_row["coachId"] in USER_ID_MAPPING:
            new_row["coachId"] = USER_ID_MAPPING[new_row["coachId"]]
        mapped_rows.append(new_row)
    mapped_local_data[table] = mapped_rows

# 2. Combine and deduplicate rows based on unique constraints
deduplicated_data = {}

# Set of preserved whopUserIds and emails in remote User table
preserved_whop_user_ids = set(r["whopUserId"] for r in remote_data.get("User", []) if r.get("whopUserId"))
preserved_emails = set(r["email"] for r in remote_data.get("User", []) if r.get("email"))

for table in tables:
    combined_rows = []
    
    # Priority 1: Remote preserved rows
    remote_rows = remote_data.get(table, [])
    # Priority 2: Mapped local rows
    local_rows = mapped_local_data.get(table, [])
    
    seen_keys = set()
    
    # Process remote first (highest priority)
    for r in remote_rows:
        # Define unique key check
        if table == "User":
            key = r["id"]
        elif table == "CoachCustomerAssignment":
            key = (r["coachId"], r["customerId"])
        elif table == "DailyCheckin":
            key = (r["customerId"], r["date"])
        elif table == "WeightLog":
            key = (r["customerId"], r["date"])
        else:
            key = r.get("id")
            
        seen_keys.add(key)
        combined_rows.append(r)
        
    # Process local (skip if unique constraint already exists in remote/seen)
    for r in local_rows:
        if table == "User":
            # Skip if ID, whopUserId, or email collisions with remote
            if r["id"] in seen_keys:
                continue
            if r.get("whopUserId") in preserved_whop_user_ids:
                continue
            if r.get("email") in preserved_emails:
                continue
            seen_keys.add(r["id"])
        elif table == "CoachCustomerAssignment":
            key = (r["coachId"], r["customerId"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
        elif table == "DailyCheckin":
            key = (r["customerId"], r["date"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
        elif table == "WeightLog":
            key = (r["customerId"], r["date"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
        else:
            key = r.get("id")
            if key and key in seen_keys:
                continue
            if key:
                seen_keys.add(key)
                
        combined_rows.append(r)
        
    deduplicated_data[table] = combined_rows
    print(f"  Table {table}: remote={len(remote_rows)}, local_mapped={len(local_rows)}, deduplicated_total={len(combined_rows)}")

# SQL generation
print("\nStep 5: Generating SQL migration file...")

DATETIME_COLUMNS = {"createdAt", "updatedAt", "startDate", "endDate"}
BOOLEAN_COLUMNS = {"isPlanPublished", "isPublic"}  # stored as INTEGER 0/1 for Prisma D1 adapter

def format_val(col_name, val):
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    # Boolean columns: always emit as 0 or 1 integer (Prisma D1 adapter requires INTEGER not BOOLEAN type)
    if col_name in BOOLEAN_COLUMNS:
        if isinstance(val, (int, float)):
            return "1" if val else "0"
        if isinstance(val, str):
            return "1" if val.lower() in ("1", "true") else "0"
        return "0"
    if col_name in DATETIME_COLUMNS:
        # Datetime column formatting
        if isinstance(val, (int, float)):
            try:
                t = float(val)
                if t > 1e11:
                    t = t / 1000.0
                from datetime import datetime, timezone
                dt = datetime.fromtimestamp(t, timezone.utc)
                fmt = "%Y-%m-%dT%H:%M:%S.%f"
                return f"'{dt.strftime(fmt)[:-3]}Z'"
            except Exception as e:
                print(f"Error formatting numeric datetime {val} for column {col_name}: {e}")
        val_str = str(val).strip()
        if val_str.isdigit():
            try:
                t = float(val_str)
                if t > 1e11:
                    t = t / 1000.0
                from datetime import datetime, timezone
                dt = datetime.fromtimestamp(t, timezone.utc)
                fmt = "%Y-%m-%dT%H:%M:%S.%f"
                return f"'{dt.strftime(fmt)[:-3]}Z'"
            except:
                pass
        if " " in val_str and "T" not in val_str:
            val_str = val_str.replace(" ", "T")
        if val_str.endswith("+00:00"):
            val_str = val_str[:-6] + "Z"
        elif val_str.endswith("+0000"):
            val_str = val_str[:-5] + "Z"
        if not val_str.endswith("Z") and "+" not in val_str and "-" not in val_str[10:]:
            val_str = val_str + "Z"
        s = val_str.replace("'", "''")
        return f"'{s}'"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).replace("'", "''")
    return f"'{s}'"

sql_lines = []
sql_lines.append("-- Auto-generated migration script")
sql_lines.append("PRAGMA foreign_keys = OFF;")

# Delete in dependency order
delete_order = [
    "WorkoutExercise", "Workout", "TrainingAssignment", "NutritionAssignment", "SupplementAssignment",
    "DailyCheckin", "WeightLog", "CoachCustomerAssignment", "Meal", "SupplementPlanItem",
    "TrainingProgram", "NutritionPlan", "SupplementPlan", "Supplement", "Exercise", "User"
]

for table in delete_order:
    sql_lines.append(f"DELETE FROM \"{table}\";")

# Insert in correct order
insert_order = [
    "User", "Exercise", "Supplement", "SupplementPlan", "SupplementPlanItem", "NutritionPlan",
    "TrainingProgram", "Meal", "CoachCustomerAssignment", "WeightLog", "DailyCheckin",
    "SupplementAssignment", "NutritionAssignment", "TrainingAssignment", "Workout", "WorkoutExercise"
]

for table in insert_order:
    sql_lines.append(f"\n-- Table: {table}")
    rows_to_insert = []
    all_rows = deduplicated_data.get(table, [])
    
    for row in all_rows:
        cols = row.keys()
        vals = [format_val(c, row[c]) for c in cols]
        cols_str = ", ".join(f"\"{c}\"" for c in cols)
        vals_str = ", ".join(vals)
        rows_to_insert.append(f"INSERT INTO \"{table}\" ({cols_str}) VALUES ({vals_str});")
        
    sql_lines.extend(rows_to_insert)

sql_lines.append("\nPRAGMA foreign_keys = ON;")

with open(MIGRATION_SQL, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print(f"SQL file generated successfully at {MIGRATION_SQL} ({len(sql_lines)} lines).")
