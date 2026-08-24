import os
import json
import dotenv
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

    print("Checking profiles/bots profiles...")
    print("-" * 80)
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
            
            # Decode token to check client_id
            client_id = None
            try:
                import base64
                parts = oauth_token.split('.')
                if len(parts) == 3:
                    payload_b64 = parts[1] + '=' * (-len(parts[1]) % 4)
                    payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
                    client_id = payload.get("client_id") or payload.get("aud")
            except Exception:
                pass

            expired = is_token_expired(oauth_token) if oauth_token else True
            
            print(f"Bot: {bot_username} ({bot_id})")
            print(f"  - Expired: {expired}")
            print(f"  - Invalid Flag: {invalid_flag}")
            print(f"  - Has Refresh Token: {bool(refresh_token)}")
            print(f"  - Issued by Client ID: {client_id}")
            
            if expired and refresh_token and not invalid_flag:
                print("  - Attempting to refresh...")
                try:
                    new_token = get_fresh_token(bot_id)
                    print(f"  - [SUCCESS] Refreshed successfully. Token expires soon? {is_token_expired(new_token)}")
                except Exception as e:
                    print(f"  - [ERROR] Failed to refresh: {e}")
            else:
                if not expired:
                    print("  - Token is valid, no refresh needed.")
                elif invalid_flag:
                    print("  - Skipping: marked as permanently invalid.")
                else:
                    print("  - Cannot refresh (no refresh token).")
            print("-" * 80)
            
        except Exception as e:
            print(f"Error checking bot {bot_id}: {e}")

if __name__ == "__main__":
    main()
