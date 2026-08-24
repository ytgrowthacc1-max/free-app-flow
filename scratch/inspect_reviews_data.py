import requests
import json

def inspect_reviews():
    company_id = "biz_G9MiyhDVcIBWMK"
    url = f"https://api.whop.com/api/v1/reviews?company_id={company_id}&limit=5"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching reviews from {url}...")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # Save a sample to file
            with open("scratch/reviews_sample.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("Successfully saved sample to scratch/reviews_sample.json")
            
            # Print structure
            reviews = data.get('data', [])
            print(f"\nTotal reviews returned: {len(reviews)}")
            page_info = data.get('page_info', {})
            print(f"Page Info: {page_info}")
            
            if reviews:
                print("\nFirst review sample:")
                first_review = reviews[0]
                for k, v in first_review.items():
                    print(f"  {k}: {v}")
        else:
            print(f"Failed: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_reviews()
