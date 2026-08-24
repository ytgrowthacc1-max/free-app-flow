import csv

def main():
    try:
        with open("scratch/whop_business_communities.csv", "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
    except FileNotFoundError:
        print("CSV file not found.")
        return
        
    print(f"Header: {header}")
    print(f"Total rows found: {len(rows)}")
    
    # Check if we have at least 50
    if len(rows) >= 50:
        print("[SUCCESS] We found at least 50 communities!")
    else:
        print(f"[WARNING] Only found {len(rows)} communities. We need at least 50.")
        
    # Print a summary of rows
    print("\n--- Summary of first 20 rows ---")
    for idx, r in enumerate(rows[:20]):
        print(f"{idx+1}. {r[0]} | Members: {r[2]} | Link: {r[1]}")
        print(f"   Reasoning: {r[5]}")
        print("-" * 50)
        
    # Print the last few rows to make sure they are correct
    print("\n--- Summary of last 5 rows ---")
    for idx, r in enumerate(rows[-5:]):
        print(f"{len(rows)-4+idx}. {r[0]} | Members: {r[2]} | Link: {r[1]}")
        print(f"   Reasoning: {r[5]}")
        print("-" * 50)

if __name__ == "__main__":
    main()
