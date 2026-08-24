import os

env_path = ".env"
new_company_id = "biz_6rZTzRAkLrBt6H"

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("WHOP_COMPANY_ID="):
            new_lines.append(f"WHOP_COMPANY_ID={new_company_id}\n")
            updated = True
            print(f"[INFO] Updated WHOP_COMPANY_ID to {new_company_id}")
        else:
            new_lines.append(line)
            
    if not updated:
        new_lines.append(f"WHOP_COMPANY_ID={new_company_id}\n")
        print(f"[INFO] Appended WHOP_COMPANY_ID={new_company_id}")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("[SUCCESS] .env file updated successfully.")
else:
    print("[ERROR] .env file not found.")
