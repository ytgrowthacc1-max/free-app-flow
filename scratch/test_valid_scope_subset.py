import requests
import urllib.parse
import sys

client_id = "app_oPIxXnyEJ8uxNK"
redirect_uri = "http://localhost:8000/callback"

# Standard comprehensive scopes for Whop apps
candidate_scopes = [
    "openid", "profile", "email",
    "company:create", "company:basic:read", "company:update", "company:balance:read",
    "experience:create", "experience:attach", "experience:detach", "experience:update",
    "forum:read", "forum:post:create",
    "chat:read", "chat:message:create", "chat:moderate",
    "support_chat:read", "support_chat:message:create", "support_chat:create",
    "dms:read", "dms:message:manage", "dms:channel:manage",
    "file:create", "file:read", "file:delete",
    "user:profile:update",
    "product:basic:read", "product:create", "product:update",
    "checkout_configuration:basic:read", "checkout_configuration:create",
    "courses:read", "courses:update",
    "affiliate:basic:read", "affiliate:create",
    "stats:read"
]

session = requests.Session()
valid = []
invalid = []

with open(".tmp/scope_results.txt", "w", encoding="utf-8") as out:
    out.write("Testing Candidate Scopes...\n")
    for s in candidate_scopes:
        url = f"https://api.whop.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={s}"
        r = session.get(url, allow_redirects=False)
        loc = r.headers.get("Location", "")
        if "error=invalid_scope" in loc:
            out.write(f"[-] INVALID: {s}\n")
            invalid.append(s)
        else:
            out.write(f"[+] VALID:   {s}\n")
            valid.append(s)
        out.flush()
        
    out.write("\n--- RESULT ---\n")
    out.write(f"Valid ({len(valid)}): {' '.join(valid)}\n")
    out.write(f"Invalid ({len(invalid)}): {' '.join(invalid)}\n")

print("Finished testing candidate scopes. Check .tmp/scope_results.txt")
