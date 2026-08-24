import json
import re
from collections import Counter

def main():
    with open(".tmp/reviews_toolsuite.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    reviews = data.get("reviews", [])
    low_reviews = data.get("low_reviews", [])
    
    print(f"Total reviews: {len(reviews)}")
    print(f"Total negative/neutral reviews (< 5 stars): {len(low_reviews)}")
    
    # Let's search for keywords in all reviews
    keywords = ["pipiads", "kalodata", "fastmoss", "shoptiktok", "tiktok", "ext", "extension", "chrome", "login", "password", "support", "work", "broken", "scam", "slow", "delay", "service", "cheap", "minea", "adsspy", "ads"]
    
    word_counts = Counter()
    for r in reviews:
        desc = (r.get("description") or "").lower()
        for kw in keywords:
            if kw in desc:
                word_counts[kw] += 1
                
    print("\nKeyword frequencies in all reviews:")
    for kw, count in word_counts.most_common():
        print(f"  {kw}: {count}")
        
    print("\n--- SAMPLE OF 5-STAR REVIEWS (What they love) ---")
    five_stars = [r for r in reviews if r.get("rating") == 5]
    for i, r in enumerate(five_stars[:15]):
        print(f"{i+1}. [{r.get('rating')} stars] (Author: {r.get('username') or r.get('user_id')}): {r.get('description')}")
        
    print("\n--- SAMPLE OF LOW-STAR REVIEWS (Pain Points) ---")
    for i, r in enumerate(low_reviews[:30]):
        print(f"{i+1}. [{r.get('rating')} stars] (Author: {r.get('username') or r.get('user_id')}): {r.get('description')}")

if __name__ == "__main__":
    main()
