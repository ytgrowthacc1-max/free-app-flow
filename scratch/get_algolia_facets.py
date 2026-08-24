import requests
import json

def get_facets():
    app_id = "QLKQ4FZ8HM"
    api_key = "edc79c87d243ec3b7368aafae5ea54db"
    
    headers = {
        "X-Algolia-Application-Id": app_id,
        "X-Algolia-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/production_products/query"
    
    payload = {
        "params": "query=&facets=[\"industry_group\",\"business_type\",\"industry_type\",\"marketplace_status\",\"is_discoverable\"]&hitsPerPage=0"
    }
    
    print("Fetching facets from Algolia...")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            facets = data.get("facets", {})
            print("\nAvailable Facets & Value Counts:")
            for facet_name, values in facets.items():
                print(f"\nFacet: {facet_name} (Unique values: {len(values)})")
                # Sort values by count descending and print top 10
                sorted_vals = sorted(values.items(), key=lambda x: x[1], reverse=True)
                for val, count in sorted_vals[:10]:
                    print(f"  - {val}: {count}")
                    
            with open("scratch/algolia_facets.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    get_facets()
