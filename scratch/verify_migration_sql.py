with open("scratch/deploy_migration.sql", "r", encoding="utf-8") as f:
    content = f.read()

checks = {
    "Delete WorkoutExercise": 'DELETE FROM "WorkoutExercise";' in content,
    "Delete User": 'DELETE FROM "User";' in content,
    "Preserved User 1": "0ebb68c1-9af5-4560-8aba-593e4b793afe" in content,
    "Preserved User 2": "9de9fd03-c894-4864-b5a7-72938c4cf64c" in content,
    "Preserved User 3": "owner-seeyoulaterleaner" in content,
    "Preserved Program 1": "91f4d177-440f-4a2a-9211-20cb46c7e31b" in content,
    "Preserved Program 2": "8a5336b6-ae24-48fe-a94d-fa7a2d9f21f2" in content,
    "Preserved Program 3": "dbd17282-36e0-4f2a-8124-cd7517e97083" in content,
}

for name, passed in checks.items():
    print(f"Check '{name}': {'PASSED' if passed else 'FAILED'}")

# Verify line count
print("Total lines:", len(content.splitlines()))
