import os
import shutil

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
marie_id = "user_GkYvyusezUmAz"
brian_id = "user_7ziL4hNckh6Ei"
company_id = "biz_g3xtLNhhkuw2dD"

marie_comp_dir = os.path.join(base_dir, "profiles", "bots", marie_id, company_id)
brian_comp_dir = os.path.join(base_dir, "profiles", "bots", brian_id, company_id)

if not os.path.exists(marie_comp_dir):
    print(f"Error: Marie's settings directory not found at {marie_comp_dir}")
    exit(1)

os.makedirs(brian_comp_dir, exist_ok=True)

files_to_copy = [
    "scheduler_settings.json", 
    "chatbot_settings.json", 
    "chatbot_instructions.md", 
    "forum_settings.json"
]

for fname in files_to_copy:
    src = os.path.join(marie_comp_dir, fname)
    dst = os.path.join(brian_comp_dir, fname)
    if os.path.exists(src):
        # We can copy the file
        shutil.copy(src, dst)
        print(f"Successfully copied {fname} from @mariesorensen to @briandelgadillo")
    else:
        print(f"Warning: {fname} not found in @mariesorensen's folder")

print("Done! Copy operation completed successfully.")
