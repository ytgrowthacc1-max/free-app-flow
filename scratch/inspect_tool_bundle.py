import os, json

print("=== Check Tool Bundle under user_mnR4EbynVY8UA ===")
path1 = r"profiles\bots\user_mnR4EbynVY8UA\biz_g3xtLNhhkuw2dD"
if os.path.exists(path1):
    print("Files in biz_g3xtLNhhkuw2dD:", os.listdir(path1))
    for fname in ["company.json", "scheduler_settings.json", "forum_settings.json", "chatbot_instructions.md"]:
        fpath = os.path.join(path1, fname)
        if os.path.exists(fpath):
            print(f"\n--- {fname} ---")
            with open(fpath, "r", encoding="utf-8") as f:
                print(f.read()[:1000])

print("\n=== Check Legacy profile tool_bundle ===")
path2 = r"profiles\tool_bundle"
if os.path.exists(path2):
    print("Files in profiles/tool_bundle:", os.listdir(path2))
    for fname in ["profile.json", "scheduler_settings.json", "forum_settings.json", "chatbot_instructions.md"]:
        fpath = os.path.join(path2, fname)
        if os.path.exists(fpath):
            print(f"\n--- {fname} ---")
            with open(fpath, "r", encoding="utf-8") as f:
                print(f.read()[:1000])
