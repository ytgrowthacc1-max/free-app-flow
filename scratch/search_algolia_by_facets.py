import requests
import json

def test_algolia_facets():
    app_id = "QLKQ4FZ8HM"
    api_key = "edc79c87d243ec3b7368aafae5ea54db"
    
    headers = {
        "X-Algolia-Application-Id": app_id,
        "X-Algolia-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/production_products/query"
    
    # Let's test filtering by industry_group or business_type
    # We will search for all products in "trading_and_investing" group with hitsPerPage=10
    payload = {
        "params": "filters=industry_group:trading_and_investing AND marketplace_status:live_marketplace&hitsPerPage=5"
    }
    
    print("Querying Algolia with filter 'industry_group:trading_and_investing'...")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Total hits matching filters: {data.get('nbHits')}")
            hits = data.get("hits", [])
            print(f"Returned hits: {len(hits)}")
            for i, h in enumerate(hits):
                print(f"\nHit {i+1}:")
                print(f"  Title: {h.get('title')}")
                print(f"  Route: {h.get('route')}")
                print(f"  Bot Name (Company): {h.get('bot_name')}")
                print(f"  Bot Tag (Company ID): {h.get('bot_tag')}")
                print(f"  Business Type: {h.get('business_type')}")
                print(f"  Industry Type: {h.get('industry_type')}")
                print(f"  Created At: {h.get('created_at')}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_algolia_facets()
