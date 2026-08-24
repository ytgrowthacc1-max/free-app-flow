import requests
import json
import re
from bs4 import BeautifulSoup

def inspect_whop_discover():
    url = "https://whop.com/discover"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find Next.js build-in JSON data
            next_data_script = soup.find('script', id='__NEXT_DATA__')
            if next_data_script:
                print("\n[SUCCESS] Found __NEXT_DATA__ script tag!")
                data = json.loads(next_data_script.string)
                print("Top-level keys in __NEXT_DATA__:", list(data.keys()))
                
                # Check for queries or page props
                props = data.get("props", {})
                print("Props keys:", list(props.keys()))
                
                page_props = props.get("pageProps", {})
                print("pageProps keys:", list(page_props.keys()))
                
                # Dump structure to a temp file for deeper inspection
                with open("scratch/next_data_structure.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Dumped full __NEXT_DATA__ JSON to scratch/next_data_structure.json")
                
                # Try to search for community / product references in the JSON structure
                json_str = json.dumps(data)
                # Count occurrences of business or product-like identifiers
                biz_ids = re.findall(r'biz_[a-zA-Z0-9]+', json_str)
                prod_ids = re.findall(r'prod_[a-zA-Z0-9]+', json_str)
                print(f"Found {len(set(biz_ids))} unique business IDs (biz_...)")
                print(f"Found {len(set(prod_ids))} unique product IDs (prod_...)")
                
                # Print a small excerpt of matches
                dehydrated_state = page_props.get("dehydratedState", {})
                if dehydrated_state:
                    print("Found react-query dehydratedState!")
                    queries = dehydrated_state.get("queries", [])
                    print(f"Number of cached queries: {len(queries)}")
                    for i, q in enumerate(queries[:5]):
                        query_key = q.get("state", {}).get("data", {})
                        print(f"Query {i} Key: {q.get('queryKey')} - Data Type: {type(query_key)}")
            else:
                print("[WARNING] __NEXT_DATA__ not found. Let's inspect the page content briefly.")
                # Print script src urls
                scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
                print("Found scripts:", scripts[:10])
        else:
            print(f"Failed to fetch page. Body: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error fetching page: {e}")

if __name__ == "__main__":
    inspect_whop_discover()
