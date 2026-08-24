import os
import json
import dotenv
import requests
from pathlib import Path

# Initialize
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR / ".env")

import sys
sys.path.append(str(BASE_DIR / "execution"))
from whop_auth import is_token_expired, get_fresh_token

def main():
    bots_dir = BASE_DIR / "profiles" / "bots"
    if not bots_dir.exists():
        print("profiles/bots directory does not exist.")
        return

    print("Re-evaluating and self-annealing all bot profiles...")
    print("=" * 80)
    
    refreshed_count = 0
    failed_count = 0
    already_valid_count = 0
    
    for bot_id in os.listdir(bots_dir):
        bot_path = bots_dir / bot_id
        if not bot_path.is_dir():
            continue
        
        pfile = bot_path / "profile.json"
        if not pfile.exists():
            continue
            
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                bot_data = json.load(f)
            
            bot_username = bot_data.get("bot_username", "Unknown Bot")
            oauth_token = bot_data.get("oauth_token", "")
            refresh_token = bot_data.get("refresh_token", "")
            invalid_flag = bot_data.get("refresh_token_invalid", False)
            
            expired = is_token_expired(oauth_token) if oauth_token else True
            
            print(f"Bot: {bot_username} ({bot_id})")
            
            if not expired:
                print("  - Status: Already Valid.")
                already_valid_count += 1
                # Ensure invalid flag is cleared since token is valid
                if invalid_flag:
                    bot_data.pop("refresh_token_invalid", None)
                    with open(pfile, "w", encoding="utf-8") as f:
                        json.dump(bot_data, f, indent=2)
                    print("  - [FIXED] Cleared invalid flag for already valid token.")
                print("-" * 80)
                continue
                
            if not refresh_token:
                print("  - Status: Expired & No Refresh Token.")
                failed_count += 1
                print("-" * 80)
                continue
                
            # Attempt refresh
            print("  - Status: Expired. Attempting to refresh...")
            # Temporarily clear invalid flag to let whop_auth try refreshing it
            if invalid_flag:
                bot_data.pop("refresh_token_invalid", None)
                with open(pfile, "w", encoding="utf-8") as f:
                    json.dump(bot_data, f, indent=2)
            
            try:
                new_token = get_fresh_token(bot_id)
                print(f"  - [SUCCESS] Refreshed token successfully!")
                refreshed_count += 1
            except Exception as e:
                err_msg = str(e)
                print(f"  - [ERROR] Failed to refresh: {err_msg}")
                # Re-apply invalid flag only if it's a permanent error
                # Check for explicit invalid_grant or invalid credentials
                is_perm_err = "invalid_grant" in err_msg.lower() or "refresh token is invalid" in err_msg.lower() or "client_secret" in err_msg.lower()
                if is_perm_err:
                    bot_data["refresh_token_invalid"] = True
                    with open(pfile, "w", encoding="utf-8") as f:
                        json.dump(bot_data, f, indent=2)
                    print("  - [MARKED] Marked as permanently invalid (invalid_grant).")
                else:
                    print("  - [SKIPPED] Temporary error. Flag left cleared to retry later.")
                failed_count += 1
            
            print("-" * 80)
            
        except Exception as e:
            print(f"Error processing bot {bot_id}: {e}")
            print("-" * 80)

    print("\nSelf-annealing summary:")
    print(f"  - Already Valid: {already_valid_count}")
    print(f"  - Refreshed successfully: {refreshed_count}")
    print(f"  - Failed/Invalid: {failed_count}")

if __name__ == "__main__":
    main()
