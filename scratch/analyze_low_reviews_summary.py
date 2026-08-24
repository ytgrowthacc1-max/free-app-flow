import json

def analyze_low_reviews():
    with open("scratch/bravosixpicks_all_reviews.json", "r", encoding="utf-8") as f:
        reviews = json.load(f)
        
    print(f"Total reviews in file: {len(reviews)}")
    
    # Remove exact duplicates based on review ID
    unique_reviews = {}
    for r in reviews:
        r_id = r.get('id')
        if r_id:
            unique_reviews[r_id] = r
            
    unique_list = list(unique_reviews.values())
    print(f"Total unique reviews: {len(unique_list)}")
    
    # Save the unique reviews
    with open("scratch/bravosixpicks_unique_reviews.json", "w", encoding="utf-8") as f:
        json.dump(unique_list, f, indent=2)
        
    # Filter for low ratings (< 5 stars)
    low_unique = [r for r in unique_list if r.get('stars', 5) < 5]
    print(f"Total unique negative/constructive reviews (< 5 stars): {len(low_unique)}")
    
    # Sort by stars
    low_unique.sort(key=lambda x: x.get('stars', 5))
    
    # Print the unique low reviews
    print("\n=============================================")
    print("        UNIQUE CONSTRUCTIVE REVIEWS          ")
    print("=============================================")
    for r in low_unique:
        reviewer = r.get('user', {}).get('username') or r.get('user', {}).get('name') or "Anonymous"
        stars = r.get('stars', 0)
        desc = r.get('description', '')
        date = r.get('created_at', '')[:10]
        print(f"\n[{date}] {stars} Stars | User: {reviewer}")
        print(f"Comment: \"{desc}\"")

if __name__ == "__main__":
    analyze_low_reviews()
