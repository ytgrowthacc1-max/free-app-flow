import requests
import json

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    company_id = "biz_BASDu66lnKwq2c"
    url = "https://api.whop.com/api/v1/experiences"
    params = {"company_id": company_id, "limit": 50}
    
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        experiences = data.get("data", [])
        print(f"\nFound {len(experiences)} Experiences/Apps for TradingPilotAI:\n")
        print(f"{'App Type':<15} | {'Experience Name':<45} | {'Experience ID':<25}")
        print("-" * 90)
        for exp in experiences:
            app_type = exp.get("app", {}).get("name") or "Unknown"
            name = exp.get("name") or "Unnamed"
            exp_id = exp.get("id")
            print(f"{app_type:<15} | {name:<45} | {exp_id:<25}")
        print("\n" + "=" * 90)
    else:
        print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    main()
