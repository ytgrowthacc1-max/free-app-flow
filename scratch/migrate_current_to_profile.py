import os
import shutil
import json
from dotenv import load_dotenv

load_dotenv()

def main():
    company_name = "Idea Engine"
    company_id = os.getenv("WHOP_COMPANY_ID")
    bot_user_id = os.getenv("BOT_USER_ID")
    oauth_token = os.getenv("WHOP_OAUTH_TOKEN")
    refresh_token = os.getenv("WHOP_REFRESH_TOKEN")

    if not company_id or not bot_user_id or not oauth_token or not refresh_token:
        print("[ERROR] Missing credentials in .env. Cannot migrate.")
        return

    slug = "idea_engine"
    profile_dir = os.path.join("profiles", slug)
    os.makedirs(profile_dir, exist_ok=True)

    profile_data = {
        "company_name": company_name,
        "company_id": company_id,
        "bot_user_id": bot_user_id,
        "oauth_token": oauth_token,
        "refresh_token": refresh_token
    }

    with open(os.path.join(profile_dir, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    # Copy defaults if not exist
    if os.path.exists("chatbot_settings.json") and not os.path.exists(os.path.join(profile_dir, "chatbot_settings.json")):
        shutil.copy("chatbot_settings.json", os.path.join(profile_dir, "chatbot_settings.json"))
    if os.path.exists(os.path.join("directives", "chatbot_instructions.md")) and not os.path.exists(os.path.join(profile_dir, "chatbot_instructions.md")):
        shutil.copy(os.path.join("directives", "chatbot_instructions.md"), os.path.join(profile_dir, "chatbot_instructions.md"))

    print(f"[SUCCESS] Created profile for {company_name} in: {profile_dir}/")

if __name__ == "__main__":
    main()
