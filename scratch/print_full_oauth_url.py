import os
import secrets
import hashlib
import base64
import urllib.parse

client_id = os.getenv("WHOP_APP_ID", "app_oPIxXnyEJ8uxNK")
redirect_uri = "http://localhost:8000/callback"

code_verifier = secrets.token_urlsafe(32)
hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')
oauth_state = secrets.token_urlsafe(16)

scopes = "ad_campaign:create ad_campaign:update affiliate:basic:read affiliate:create affiliate:update ai_prompt:create stats:read experience:attach experience:create experience:delete experience:detach experience:hidden_experience:read experience:update company:log:read chat:moderate chat:message:create chat:read dms:read dms:message:manage dms:channel:manage custom_emoji:update checkout_configuration:basic:read checkout_configuration:create checkout_configuration:delete company:balance:read company:manage_checkout company:basic:read company:create company:update social_link:update courses:read courses:update course_lesson_interaction:read course_analytics:read developer:basic:read developer:create_app developer:manage_builds developer:update_app forum:post:create forum:read membership:basic:read membership:cancel membership:manage membership:terminate payment:basic:read payout:create payout:delete file:create file:delete file:read product:basic:read product:create product:delete product:update push_notification:send promo_code:create promo_code:delete promo_code:update user:profile:update support_chat:create support_chat:read support_chat:message:create"

params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": scopes,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "state": oauth_state
}

auth_url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
print("URL:", auth_url)
print("\nVerifier:", code_verifier)
