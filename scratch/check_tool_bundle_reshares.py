import os, json

master_ss_path = r"profiles\bots\user_mnR4EbynVY8UA\biz_g3xtLNhhkuw2dD\scheduler_settings.json"
if os.path.exists(master_ss_path):
    with open(master_ss_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("reshare_enabled:", data.get("reshare_enabled"))
    reshare_ids = data.get("reshare_experience_ids", [])
    print(f"Total reshare target experience IDs configured: {len(reshare_ids)}")
    print("Sample reshare IDs:", reshare_ids[:5])
else:
    print("File not found")
