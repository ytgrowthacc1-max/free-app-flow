import requests
import urllib.parse

client_id = "app_oPIxXnyEJ8uxNK"
redirect_uri = "http://localhost:8000/callback"

all_scopes = ["ad_campaign:create","ad_campaign:update","affiliate:basic:read","affiliate:create","affiliate:update","ai_prompt:create","stats:read","experience:attach","experience:create","experience:delete","experience:detach","experience:hidden_experience:read","experience:update","company:log:read","chat:moderate","chat:message:create","chat:read","dms:read","dms:message:manage","dms:channel:manage","custom_emoji:update","checkout_configuration:basic:read","checkout_configuration:create","checkout_configuration:delete","company:balance:read","company:manage_checkout","company:basic:read","company:update","social_link:update","courses:read","courses:update","course_lesson_interaction:read","course_analytics:read","developer:basic:read","developer:create_app","developer:manage_builds","developer:update_app","forum:post:create","forum:read","membership:basic:read","membership:cancel","membership:manage","membership:terminate","payment:basic:read","payout:create","payout:delete","file:create","file:delete","file:read","product:basic:read","product:create","product:delete","product:update","push_notification:send","promo_code:create","promo_code:delete","promo_code:update","user:profile:update","support_chat:create","support_chat:read","support_chat:message:create","company:create"]

valid = []
invalid = []

session = requests.Session()
# Whop redirects invalid scope immediately to redirect_uri with error=invalid_scope
for scope in all_scopes:
    url = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={scope}"
    r = session.get(url, allow_redirects=False)
    loc = r.headers.get("Location", "")
    if "error=invalid_scope" in loc:
        invalid.append(scope)
    else:
        valid.append(scope)

print(f"Tested {len(all_scopes)} scopes.")
print("Valid Scopes Count:", len(valid))
print("Valid Scopes String:")
valid_str = " ".join(valid)
print(valid_str)
print("\nInvalid Scopes:", invalid)

# Test combined valid_str
url_all = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={urllib.parse.quote(valid_str)}"
r_all = session.get(url_all, allow_redirects=False)
loc_all = r_all.headers.get("Location", "")
if "error=invalid_scope" in loc_all:
    print("\nCombined Valid Scopes Test: FAILED (Location:", loc_all, ")")
else:
    print("\nCombined Valid Scopes Test: SUCCESS! (Location:", loc_all, ")")
