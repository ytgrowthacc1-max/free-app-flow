import subprocess
import json

WRANGLER_CONFIG = "../Health_APP_WHOP/wrangler.toml"
CWD = r"c:\Python\WHOP AUTOMATION AGENTIC"

def run_d1_file(sql_file):
    cmd = f'npx wrangler d1 execute DB --remote --file="{sql_file}" --config={WRANGLER_CONFIG}'
    res = subprocess.run(cmd, capture_output=True, cwd=CWD, shell=True)
    out = res.stdout.decode("utf-8", errors="replace")
    err = res.stderr.decode("utf-8", errors="replace")
    if res.returncode != 0:
        print("ERROR:", err[:800])
        return False
    print("OK:", out[-300:] if len(out) > 300 else out)
    return True

# Write the fix SQL to a temp file
fix_sql = r"""
PRAGMA foreign_keys = OFF;

-- ============================================================
-- Fix 1: User.isPlanPublished - BOOLEAN stored as 0/1 integer
-- ============================================================
ALTER TABLE "User" RENAME TO "User_old";

CREATE TABLE "User" (
    "id"               TEXT     NOT NULL PRIMARY KEY,
    "createdAt"        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt"        DATETIME NOT NULL,
    "whopUserId"       TEXT     NOT NULL,
    "email"            TEXT     NOT NULL,
    "name"             TEXT,
    "avatarUrl"        TEXT,
    "role"             TEXT     NOT NULL DEFAULT 'CUSTOMER',
    "isPlanPublished"  INTEGER  NOT NULL DEFAULT 0
);

INSERT INTO "User" ("id","createdAt","updatedAt","whopUserId","email","name","avatarUrl","role","isPlanPublished")
SELECT "id","createdAt","updatedAt","whopUserId","email","name","avatarUrl","role",
       CASE WHEN "isPlanPublished" = 1 OR "isPlanPublished" = 'true' OR "isPlanPublished" = 'True' THEN 1 ELSE 0 END
FROM "User_old";

DROP TABLE "User_old";

CREATE UNIQUE INDEX IF NOT EXISTS "User_whopUserId_key" ON "User"("whopUserId");
CREATE UNIQUE INDEX IF NOT EXISTS "User_email_key" ON "User"("email");

-- ============================================================
-- Fix 2: TrainingProgram.isPublic - BOOLEAN stored as 0/1 integer
-- ============================================================
ALTER TABLE "TrainingProgram" RENAME TO "TrainingProgram_old";

CREATE TABLE "TrainingProgram" (
    "id"          TEXT     NOT NULL PRIMARY KEY,
    "createdAt"   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt"   DATETIME NOT NULL,
    "ownerId"     TEXT     NOT NULL,
    "name"        TEXT     NOT NULL,
    "description" TEXT,
    "level"       TEXT,
    "isPublic"    INTEGER  NOT NULL DEFAULT 0,
    CONSTRAINT "TrainingProgram_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO "TrainingProgram" ("id","createdAt","updatedAt","ownerId","name","description","level","isPublic")
SELECT "id","createdAt","updatedAt","ownerId","name","description","level",
       CASE WHEN "isPublic" = 1 OR "isPublic" = 'true' OR "isPublic" = 'True' THEN 1 ELSE 0 END
FROM "TrainingProgram_old";

DROP TABLE "TrainingProgram_old";

PRAGMA foreign_keys = ON;
"""

sql_file = "scratch/fix_boolean_columns.sql"
with open(sql_file, "w") as f:
    f.write(fix_sql)

print("Applying boolean column fixes to D1...")
success = run_d1_file(sql_file)
if success:
    print("\nSuccess! Verifying column types...")
    
    def run_d1(sql):
        cmd = f'npx wrangler d1 execute DB --remote --command="{sql}" --config={WRANGLER_CONFIG} --json'
        res = subprocess.run(cmd, capture_output=True, cwd=CWD, shell=True)
        out = res.stdout.decode("utf-8", errors="replace")
        try:
            return json.loads(out)[0].get("results", [])
        except:
            return []

    rows = run_d1("PRAGMA table_info('User')")
    for r in rows:
        if r.get("name") in ("isPlanPublished", "role"):
            print(f"  User.{r['name']}: type={r['type']}")
    
    rows = run_d1("PRAGMA table_info('TrainingProgram')")
    for r in rows:
        if r.get("name") == "isPublic":
            print(f"  TrainingProgram.{r['name']}: type={r['type']}")

    rows = run_d1("SELECT COUNT(*) as cnt FROM User")
    print(f"  User count after fix: {rows[0].get('cnt') if rows else 'ERR'}")
    
    rows = run_d1("SELECT COUNT(*) as cnt FROM TrainingProgram")
    print(f"  TrainingProgram count after fix: {rows[0].get('cnt') if rows else 'ERR'}")
else:
    print("Fix failed!")
