import os
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv("WHOP_API_KEY", "")
    app_id = os.getenv("WHOP_APP_ID", "")
    comp_id = os.getenv("WHOP_COMPANY_ID", "")
    bot_id = os.getenv("BOT_USER_ID", "")
    oauth_token = os.getenv("WHOP_OAUTH_TOKEN", "")

    print("=== .env Configuration Inspection ===")
    print(f"WHOP_API_KEY present: {bool(api_key)}")
    if api_key:
        print(f"  Prefix: {api_key[:8]}...")
        print(f"  Length: {len(api_key)}")
    print(f"WHOP_APP_ID: {app_id}")
    print(f"WHOP_COMPANY_ID: {comp_id}")
    print(f"BOT_USER_ID: {bot_id}")
    print(f"WHOP_OAUTH_TOKEN present: {bool(oauth_token)}")
    if oauth_token:
        print(f"  Prefix: {oauth_token[:15]}...")

if __name__ == "__main__":
    main()
