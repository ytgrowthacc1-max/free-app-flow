import requests
import json

def test_endpoint(url, params=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    print(f"Testing URL: {url}")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"  Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"  Keys: {keys}")
                # Print sample data
                for k in keys:
                    v = data[k]
                    if isinstance(v, list):
                        print(f"    Key '{k}' is a list with {len(v)} items. Sample: {v[:2]}")
            else:
                print(f"  Received list of length: {len(data)}")
                print(f"  Sample: {data[:2]}")
            return data
        else:
            print(f"  Failed: {resp.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")
    return None

def main():
    company_id = "biz_BASDu66lnKwq2c"
    
    # 1. Test company products endpoint
    test_endpoint(f"https://api.whop.com/api/v1/companies/{company_id}/products")
    
    # 2. Test products search endpoint
    test_endpoint("https://api.whop.com/api/v1/products", params={"company_id": company_id})
    
    # 3. Test company experiences endpoint
    test_endpoint(f"https://api.whop.com/api/v1/companies/{company_id}/experiences")
    
    # 4. Test experiences list endpoint
    test_endpoint("https://api.whop.com/api/v1/experiences", params={"company_id": company_id})

if __name__ == "__main__":
    main()
