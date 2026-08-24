import json

def generate_clean_report():
    with open("scratch/bravosixpicks_all_reviews.json", "r", encoding="utf-8") as f:
        reviews = json.load(f)
        
    unique_reviews = {}
    for r in reviews:
        r_id = r.get('id')
        if r_id:
            unique_reviews[r_id] = r
            
    unique_list = list(unique_reviews.values())
    low_unique = [r for r in unique_list if r.get('stars', 5) < 5]
    
    report = {
        "total_crawled": len(reviews),
        "total_unique": len(unique_list),
        "total_low": len(low_unique),
        "low_reviews": []
    }
    
    # Clean up low reviews data for reporting
    for r in low_unique:
        report["low_reviews"].append({
            "id": r.get('id'),
            "stars": r.get('stars'),
            "username": r.get('user', {}).get('username') or r.get('user', {}).get('name') or "Anonymous",
            "date": r.get('created_at', '')[:10],
            "description": r.get('description', '').strip()
        })
        
    with open("scratch/bravosixpicks_cleaned_low_reviews.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Analysis completed: {len(low_unique)} unique low reviews extracted and cleaned.")

if __name__ == "__main__":
    generate_clean_report()
