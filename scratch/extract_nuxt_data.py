import requests
import json
import re
from bs4 import BeautifulSoup

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    url = "https://whop.com/tpai/"
    print(f"Fetching: {url}")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch page: {resp.status_code}")
        return
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 1. Search for Nuxt data scripts
    nuxt_data = soup.find('script', id='__NUXT_DATA__')
    if nuxt_data:
        print("Found __NUXT_DATA__ script tag!")
        try:
            parsed = json.loads(nuxt_data.string)
            # Nuxt data is a serialized array/graph of values
            with open(".tmp/nuxt_data_raw.json", "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            print("Saved raw Nuxt state array to .tmp/nuxt_data_raw.json")
            
            # Let's search for price-like numbers or product terms in the Nuxt array
            strings_found = []
            for item in parsed:
                if isinstance(item, str):
                    if len(item) > 2 and ("price" in item.lower() or "prod_" in item or "plan_" in item or "recur" in item or "month" in item or "$" in item):
                        strings_found.append(item)
            print(f"Sample of interesting string values in Nuxt state: {strings_found[:30]}")
        except Exception as e:
            print(f"Failed to parse __NUXT_DATA__: {e}")
            
    # 2. Search for any script tags containing window.__NUXT__
    for script in soup.find_all('script'):
        if script.string and ('window.__NUXT__' in script.string or 'nuxt' in script.string.lower()):
            print("Found inline script containing Nuxt/State variables!")
            with open(".tmp/inline_script_nuxt.txt", "w", encoding="utf-8") as f:
                f.write(script.string)
            print("Saved inline script to .tmp/inline_script_nuxt.txt")
            break

    # 3. Simple regex search on whole HTML for plans or pricing terms
    # Look for "prod_" or "plan_" or "price" details
    print("\nRegex searching raw HTML for product ids and names...")
    prod_ids = set(re.findall(r'prod_[a-zA-Z0-9]+', resp.text))
    plan_ids = set(re.findall(r'plan_[a-zA-Z0-9]+', resp.text))
    prices = set(re.findall(r'"price":\s*(\d+)', resp.text))
    print(f"Found Product IDs: {prod_ids}")
    print(f"Found Plan IDs: {plan_ids}")
    print(f"Found prices: {prices}")

if __name__ == "__main__":
    main()
