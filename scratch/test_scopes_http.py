import requests
import urllib.parse
import os

client_id = "app_oPIxXnyEJ8uxNK"
redirect_uri = "http://localhost:8000/callback"

# Clean parent.lock files in profiles
profiles_dir = r"C:\Python\Browsing Skill Agent\.profiles"
if os.path.exists(profiles_dir):
    for root, dirs, files in os.walk(profiles_dir):
        for file in files:
            if file in ("parent.lock", "lockfile"):
                p = os.path.join(root, file)
                try:
                    os.remove(p)
                    print(f"Removed lock file: {p}")
                except Exception:
                    pass

all_scopes = [
    "ad_campaign:create","ad_campaign:update","affiliate:basic:read","affiliate:create","affiliate:update","ai_prompt:create","stats:read","experience:attach","experience:create","experience:delete","experience:detach","experience:hidden_experience:read","experience:update","company:log:read","chat:moderate","chat:message:create","chat:read","dms:read","dms:message:manage","dms:channel:manage","custom_emoji:update","checkout_configuration:basic:read","checkout_configuration:create","checkout_configuration:delete","company:balance:read","company:manage_checkout","company:basic:read","company:update","social_link:update","courses:read","courses:update","course_lesson_interaction:read","course_analytics:read","developer:basic:read","developer:create_app","developer:manage_builds","developer:update_app","forum:post:create","forum:read","membership:basic:read","membership:cancel","membership:manage","membership:terminate","payment:basic:read","payout:create","payout:delete","file:create","file:delete","file:read","product:basic:read","product:create","product:delete","product:update","push_notification:send","promo_code:create","promo_code:delete","promo_code:update","user:profile:update","support_chat:create","support_chat:read","support_chat:message:create","company:create"
]

print("Removed all lock files.")
