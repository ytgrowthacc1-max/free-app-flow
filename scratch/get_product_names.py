import requests
import json

def get_product_details(prod_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://api.whop.com/api/v1/products/{prod_id}"
    print(f"Fetching: {url}")
    resp = requests.get(url, headers=headers)
    print(f"  Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"  Error: {resp.text[:500]}")

def main():
    product_ids = [
        "prod_idrEecSloni51",
        "prod_T6Icayc7fXnLF",
        "prod_vh0ZNaCvmLmKZ"
    ]
    for pid in product_ids:
        print("=" * 60)
        get_product_details(pid)
        print("=" * 60)

if __name__ == "__main__":
    main()
