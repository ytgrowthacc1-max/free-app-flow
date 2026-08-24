import requests
import re

def get_product_page(slug):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://whop.com/tpai/checkout/{slug}/"
    print(f"Fetching checkout page: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            html = resp.text
            # Look for price information in JSONLD or window.__nuxt__ or scripts
            # Or use a simple regex to find currency symbols and numbers
            prices = re.findall(r'"price":\s*(\d+(?:\.\d{2})?)', html)
            currency = re.findall(r'"priceCurrency":\s*"([A-Z]{3})"', html)
            desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
            
            desc = desc_match.group(1) if desc_match else "No description found"
            price_str = f"{currency[0]} {prices[0]}" if (prices and currency) else "Check URL"
            
            # Let's also look for text patterns like "$XX / month" or similar
            matches = re.findall(r'\$\d+(?:\.\d{2})?\s*(?:/\s*(?:month|year|week)|one-time)?', html)
            unique_matches = list(set(matches))
            
            print(f"  Detected Price (Metadata): {price_str}")
            print(f"  Pricing text found: {unique_matches}")
            print(f"  Description: {desc[:150]}...")
        else:
            print(f"  Failed to fetch: {resp.status_code}")
    except Exception as e:
        print(f"  Exception: {e}")

def main():
    product_slugs = [
        "ai-trading-vip",
        "hexr-pro-41",
        "vip-tradingpilotai-discord-access"
    ]
    for slug in product_slugs:
        print("-" * 50)
        get_product_page(slug)
        print("-" * 50)

if __name__ == "__main__":
    main()
