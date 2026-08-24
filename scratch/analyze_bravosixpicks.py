import requests
import json
import os
import sys

# Ensure Windows terminal doesn't crash on emojis/unicode characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_community():
    slug = "bravosixpicks"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    # 1. Fetch Company details
    company_url = f"https://api.whop.com/api/v1/companies/{slug}"
    print(f"Fetching company details from: {company_url}")
    try:
        comp_resp = requests.get(company_url, headers=headers, timeout=10)
        if comp_resp.status_code != 200:
            print(f"Failed to fetch company details: {comp_resp.status_code}")
            print(comp_resp.text)
            return
            
        company_data = comp_resp.json()
        print("\n--- COMPANY PROFILE ---")
        print(f"ID: {company_data.get('id')}")
        print(f"Title: {company_data.get('title')}")
        print(f"Description: {company_data.get('description')}")
        print(f"Members: {company_data.get('member_count')}")
        print(f"Reviews Count: {company_data.get('published_reviews_count')}")
        print(f"Verified: {company_data.get('verified')}")
        print(f"Social Links: {company_data.get('social_links')}")
        print(f"Owner: {company_data.get('owner_user')}")
        
        company_id = company_data.get('id')
        if not company_id:
            print("Error: Could not extract company_id")
            return
            
        # 2. Fetch Reviews (handling paging if needed)
        reviews_url = f"https://api.whop.com/api/v1/reviews?company_id={company_id}&limit=100"
        print(f"\nFetching reviews from: {reviews_url}")
        rev_resp = requests.get(reviews_url, headers=headers, timeout=10)
        
        if rev_resp.status_code != 200:
            print(f"Failed to fetch reviews: {rev_resp.status_code}")
            return
            
        reviews_data = rev_resp.json()
        reviews = reviews_data.get('data', [])
        print(f"Retrieved {len(reviews)} reviews.")
        
        # Save raw data to file
        output = {
            "company": company_data,
            "reviews": reviews
        }
        os.makedirs("scratch", exist_ok=True)
        with open("scratch/bravosixpicks_data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print("Saved raw data to scratch/bravosixpicks_data.json")
        
        # 3. Analyze rating distribution
        ratings = [r.get('stars', 0) for r in reviews]
        dist = {i: ratings.count(i) for i in range(1, 6)}
        print("\n--- RATING DISTRIBUTION ---")
        for stars, count in dist.items():
            print(f"  {stars} Stars: {count} reviews")
            
        # 4. Print reviews with critical feedback (1-4 stars) or long constructive comments
        print("\n--- CONSTRUCTIVE / CRITICAL FEEDBACK ---")
        critical_reviews = [r for r in reviews if r.get('stars', 5) < 5 or (r.get('description') and len(r.get('description', '')) > 100)]
        
        print(f"Found {len(critical_reviews)} reviews with detailed or critical feedback.")
        for idx, rev in enumerate(critical_reviews[:15]): # Print first 15 critical/detailed reviews
            reviewer = rev.get('user', {}).get('username') or rev.get('user', {}).get('name') or "Anonymous"
            stars = rev.get('stars', 0)
            desc = rev.get('description', '')
            date = rev.get('created_at', '')[:10]
            print(f"\n[{date}] Reviewer: {reviewer} | Rating: {stars} Stars")
            print(f"Comment: \"{desc}\"")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_community()
