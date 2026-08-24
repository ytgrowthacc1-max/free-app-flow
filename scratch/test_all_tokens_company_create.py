import os
import json
import requests

def test_tokens():
    bots_dir = os.path.join("profiles", "bots")
    results = []
    
    # Check bot profiles
    for bot_folder in os.listdir(bots_dir):
        profile_path = os.path.join(bots_dir, bot_folder, "profile.json")
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            token = data.get("oauth_token")
            username = data.get("bot_username", bot_folder)
            bot_id = data.get("bot_user_id", bot_folder)
            
            if token:
                res = requests.post(
                    "https://api.whop.com/api/v1/companies",
                    json={"title": "Test Scope Company Check", "send_customer_emails": False},
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                )
                status = res.status_code
                resp_text = res.text[:200]
                print(f"[{username} / {bot_id}] Status: {status} -> {resp_text}")
                results.append({
                    "username": username,
                    "bot_id": bot_id,
                    "status": status,
                    "response": resp_text
                })

    # Check env WHOP_API_KEY
    company_key = os.getenv("WHOP_API_KEY")
    if company_key:
        res = requests.post(
            "https://api.whop.com/api/v1/companies",
            json={"title": "Test Scope Company Check", "send_customer_emails": False},
            headers={"Authorization": f"Bearer {company_key}", "Content-Type": "application/json"}
        )
        print(f"[WHOP_API_KEY] Status: {res.status_code} -> {res.text[:200]}")
        results.append({
            "username": "WHOP_API_KEY",
            "status": res.status_code,
            "response": res.text[:200]
        })

    with open(".tmp/test_tokens_company_create_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    test_tokens()
