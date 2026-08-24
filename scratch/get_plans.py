import requests
import json

def get_product_plans(prod_id, prod_title):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = "https://api.whop.com/api/v1/plans"
    params = {"product_id": prod_id}
    print(f"Fetching plans for product '{prod_title}' ({prod_id})...")
    resp = requests.get(url, headers=headers, params=params)
    print(f"  Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        plans = data.get("data", [])
        print(f"  Found {len(plans)} plans:")
        for plan in plans:
            plan_id = plan.get("id")
            plan_name = plan.get("name") or "Standard"
            
            # Extract price and billing terms
            pricing_type = plan.get("billing_type") # e.g. recurring, one_time
            price = plan.get("price")
            currency = plan.get("currency") or "USD"
            interval = plan.get("interval")
            interval_count = plan.get("interval_count")
            
            pricing_info = f"{price} {currency}"
            if pricing_type == "recurring":
                pricing_info += f" every {interval_count} {interval}(s)"
            elif pricing_type == "one_time":
                pricing_info += " (one-time)"
            else:
                pricing_info += f" ({pricing_type})"
                
            print(f"    - [{plan_id}] {plan_name}: {pricing_info}")
    else:
        print(f"  Error: {resp.text[:500]}")

def main():
    products = [
        {"id": "prod_idrEecSloni51", "title": "HEXR PRO"},
        {"id": "prod_T6Icayc7fXnLF", "title": "TRADINGPILOTAI"},
        {"id": "prod_vh0ZNaCvmLmKZ", "title": "VIP TradingPilotAI Discord Access"}
    ]
    for p in products:
        print("=" * 60)
        get_product_plans(p["id"], p["title"])
        print("=" * 60)

if __name__ == "__main__":
    main()
