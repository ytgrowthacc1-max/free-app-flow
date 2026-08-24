import os
import sys
import json
from dotenv import load_dotenv

# Ensure the execution directory is in the import path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, "execution"))

try:
    from whop_auth import get_fresh_token
except ImportError:
    from execution.whop_auth import get_fresh_token

load_dotenv()

def main():
    bots_dir = os.path.join(base_dir, "profiles", "bots")
    if not os.path.exists(bots_dir):
        print(f"[ERROR] Bots directory does not exist: {bots_dir}")
        return
    
    bot_folders = sorted([f for f in os.listdir(bots_dir) if os.path.isdir(os.path.join(bots_dir, f))])
    
    print(f"Scanning {len(bot_folders)} bot folders...")
    
    valid_bots = []
    invalid_bots = []
    skipped_bots = []
    
    for folder in bot_folders:
        pfile = os.path.join(bots_dir, folder, "profile.json")
        if not os.path.exists(pfile):
            continue
            
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            bot_user_id = data.get("bot_user_id")
            bot_username = data.get("bot_username")
            refresh_token = data.get("refresh_token")
            
            if not bot_user_id or not refresh_token:
                skipped_bots.append((folder, "missing IDs or refresh token"))
                continue
                
            if data.get("refresh_token_invalid"):
                skipped_bots.append((bot_username or bot_user_id, "marked invalid in profile"))
                continue
                
            token = get_fresh_token(bot_user_id)
            if token:
                valid_bots.append(bot_username or bot_user_id)
            else:
                invalid_bots.append(bot_username or bot_user_id)
        except Exception as e:
            invalid_bots.append(folder)
            
    print("\n=== SUMMARY ===")
    print(f"Total folders checked: {len(bot_folders)}")
    print(f"Valid / Authorized Bots ({len(valid_bots)}):")
    for idx, bot in enumerate(valid_bots):
        print(f"  {idx+1}. {bot}")
        
    print(f"\nInvalid / Expired Bots ({len(invalid_bots)}):")
    for idx, bot in enumerate(invalid_bots):
        print(f"  {idx+1}. {bot}")
        
    print(f"\nSkipped / Flagged Bots ({len(skipped_bots)}):")
    for idx, (bot, reason) in enumerate(skipped_bots):
        print(f"  {idx+1}. {bot} ({reason})")

if __name__ == "__main__":
    main()
