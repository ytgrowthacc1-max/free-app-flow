import os
import sys
import time
import secrets
import hashlib
import base64
import urllib.parse
import json
import requests

# Add browser skill path if available
sys.path.append(r"C:\Python\Browsing Skill Agent\execution")

def get_whop_auth_url():
    client_id = "app_oPIxXnyEJ8uxNK"
    redirect_uri = "http://localhost:8000/callback"
    code_verifier = secrets.token_urlsafe(32)
    hash_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').replace('=', '')

    scopes = "openid profile email company:create company:basic:read user:profile:update experience:create app_authorization:create forum:read forum:post:create chat:read chat:message:create support_chat:read support_chat:message:create dms:read dms:message:manage"
    oauth_state = secrets.token_urlsafe(16)
    oauth_nonce = secrets.token_urlsafe(16)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": oauth_state,
        "nonce": oauth_nonce
    }
    url = "https://api.whop.com/oauth/authorize?" + urllib.parse.urlencode(params)
    return url, client_id, redirect_uri, code_verifier

def create_all_communities(token):
    manifest_path = os.path.join("config", "proposed_communities_donnajacksona7.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        communities = json.load(f)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    created_results = []
    base_dir = os.path.join("profiles", "bots", "user_gAkQk98I3AyP4")

    for index, comm in enumerate(communities, start=1):
        print(f"[{index}/20] Creating community: {comm['title']}...")
        payload = {
            "title": comm["title"],
            "description": comm["description"],
            "send_customer_emails": False
        }
        res = requests.post("https://api.whop.com/api/v1/companies", json=payload, headers=headers)
        if res.status_code in (200, 201):
            data = res.json()
            company_id = data.get("id")
            route = data.get("route")
            print(f"  -> SUCCESS! Company ID: {company_id}, Route: {route}")
            
            item = {
                "id": company_id,
                "title": comm["title"],
                "route": route,
                "tagline": comm["tagline"],
                "description": comm["description"],
                "target_niche": comm["target_niche"],
                "status": "created_live",
                "raw": data
            }
            created_results.append(item)

            # Move or copy staged dir to real biz_ID
            staged_dir = os.path.join(base_dir, f"staged_{comm['route']}")
            biz_dir = os.path.join(base_dir, company_id)
            if os.path.exists(staged_dir):
                if os.path.exists(biz_dir):
                    import shutil
                    shutil.rmtree(biz_dir)
                os.rename(staged_dir, biz_dir)
                # Update community_config.json inside biz_dir
                cfg_path = os.path.join(biz_dir, "community_config.json")
                with open(cfg_path, "w", encoding="utf-8") as cfg_f:
                    json.dump(item, cfg_f, indent=2)
        else:
            print(f"  -> FAILED ({res.status_code}): {res.text[:200]}")
            created_results.append({
                "title": comm["title"],
                "status": "failed",
                "error": res.text[:200]
            })

    output_path = os.path.join(".tmp", "created_20_communities_report.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(created_results, f, indent=2)

    print(f"\nCompleted creation process. Report saved to {output_path}")

if __name__ == "__main__":
    profile_path = os.path.join("profiles", "bots", "user_gAkQk98I3AyP4", "profile.json")
    token = None
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            token = data.get("oauth_token")

    if not token:
        print("No token found in profile.json!")
        sys.exit(1)

    print("Attempting creation with existing token...")
    # Test single call
    test_res = requests.post(
        "https://api.whop.com/api/v1/companies",
        json={"title": "Test Company Check"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )

    if test_res.status_code in (200, 201):
        print("Token has company:create permission! Starting batch creation...")
        create_all_communities(token)
    else:
        print(f"Token missing permission or error ({test_res.status_code}): {test_res.text[:200]}")
        url, client_id, redirect_uri, code_verifier = get_whop_auth_url()
        print("\nRe-authorization URL generated:")
        print(url)
