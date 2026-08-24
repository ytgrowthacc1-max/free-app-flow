import sqlite3

conn = sqlite3.connect("c:/Python/Health_APP_WHOP/prisma/dev.db")
cursor = conn.cursor()

queries = {
    "DailyCheckin": "SELECT count(*) FROM DailyCheckin WHERE customerId = 'cmn3po9zq0000ib04bbcma3ge';",
    "WeightLog": "SELECT count(*) FROM WeightLog WHERE customerId = 'cmn3po9zq0000ib04bbcma3ge';",
    "TrainingAssignment": "SELECT count(*), trainingProgramId FROM TrainingAssignment WHERE customerId = 'cmn3po9zq0000ib04bbcma3ge';",
    "CoachCustomerAssignment": "SELECT count(*) FROM CoachCustomerAssignment WHERE customerId = 'cmn3po9zq0000ib04bbcma3ge';",
}

for name, q in queries.items():
    cursor.execute(q)
    res = cursor.fetchall()
    print(f"Local {name}: {res}")

conn.close()
