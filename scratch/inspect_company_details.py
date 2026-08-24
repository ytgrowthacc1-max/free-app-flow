import requests
import json

def inspect_details():
    # Let's test with 'crystal-academy' or 'teampow'
    slug = "crystal-academy"
    url = f"https://api.whop.com/api/v1/companies/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching company details from {url}...")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("\nCompany Details Keys:")
            print(list(data.keys()))
            
            # Print a clean version of the data
            print("\nSelected Details:")
            for k in ['id', 'title', 'route', 'description', 'member_count', 'published_reviews_count', 'social_links', 'verified', 'target_audience']:
                print(f"  {k}: {data.get(k)}")
                
            # Check if there is a nested reviews or ratings block
            if 'reviews' in data:
                print("\nFound nested reviews!")
                print(data['reviews'])
            else:
                print("\nNo nested 'reviews' key found in company details.")
                
            # Let's write the full response to a file
            with open("scratch/company_details_sample.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("Full response saved to scratch/company_details_sample.json")
            
            # Now let's guess and test reviews endpoints:
            company_id = data.get('id')
            print(f"\nTesting candidate reviews endpoints for Company ID: {company_id} and Slug: {slug}...")
            
            candidates = [
                f"https://api.whop.com/api/v1/companies/{slug}/reviews",
                f"https://api.whop.com/api/v1/companies/{company_id}/reviews",
                f"https://api.whop.com/api/v1/reviews?company_id={company_id}",
                f"https://api.whop.com/api/v1/reviews?company={slug}",
                f"https://whop.com/api/v2/reviews?company_id={company_id}",
                f"https://whop.com/api/v2/companies/{slug}/reviews"
            ]
            
            for c_url in candidates:
                print(f"Testing: {c_url}")
                r = requests.get(c_url, headers=headers, timeout=5)
                print(f"  Status: {r.status_code}")
                if r.status_code == 200:
                    print(f"  [SUCCESS] Found reviews endpoint!")
                    try:
                        r_data = r.json()
                        print(f"  Keys in reviews response: {list(r_data.keys()) if isinstance(r_data, dict) else type(r_data)}")
                        if isinstance(r_data, dict) and 'reviews' in r_data:
                            print(f"  Total reviews count: {len(r_data['reviews'])}")
                            if r_data['reviews']:
                                print(f"  Sample review: {r_data['reviews'][0]}")
                        elif isinstance(r_data, list):
                            print(f"  Total reviews in list: {len(r_data)}")
                            if r_data:
                                print(f"  Sample review: {r_data[0]}")
                    except Exception as ex:
                        print(f"  Error parsing json: {ex}")
                        
        else:
            print(f"Failed to fetch details: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_details()
