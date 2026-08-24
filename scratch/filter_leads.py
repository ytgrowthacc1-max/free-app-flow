import json
import sys

# Ensure UTF-8 printing on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def main():
    try:
        with open("scratch/business_owner_leads.json", "r", encoding="utf-8") as f:
            leads = json.load(f)
    except FileNotFoundError:
        print("JSON file not found.")
        return
        
    print(f"Total leads: {len(leads)}")
    
    # Filter for >= 1000 members
    big_leads = [l for l in leads if l.get("members", 0) >= 1000]
    print(f"Leads with >= 1000 members: {len(big_leads)}")
    
    # Print the first 10 big leads
    for i, l in enumerate(big_leads[:20]):
        print(f"{i+1}. {l['name']} - Members: {l['members']} - Reviews: {l['reviews']} - Category: {l['category']}")
        print(f"   Link: {l['link']}")
        desc = l.get('description', '') or ''
        print(f"   Desc: {desc[:150]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()
