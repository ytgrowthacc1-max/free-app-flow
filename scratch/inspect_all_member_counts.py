import re
import json

def main():
    with open(".tmp/full_rsc_payload.txt", "r", encoding="utf-8") as f:
        payload = f.read()
        
    print(f"RSC Payload size: {len(payload)}")
    
    # 1. Let's find all occurrences of "memberCount" or "member_count" or similar patterns
    patterns = [
        r'"memberCount"\s*:\s*\d+',
        r'"member_count"\s*:\s*\d+',
        r'"members"\s*:\s*\d+',
        r'"subscriberCount"\s*:\s*\d+'
    ]
    
    for p in patterns:
        matches = re.findall(p, payload)
        print(f"Matches for pattern '{p}': {len(matches)}")
        print(f"  Values: {list(set(matches))[:10]}")

    # 2. Let's print the JSON structure surrounding the products
    # Search for all occurrences of product blocks: {"id":"prod_...", "title":"..."}
    prod_blocks = re.findall(r'(\{"id"\s*:\s*"prod_[^"]+".*?\})', payload)
    print(f"\nFound {len(prod_blocks)} potential product blocks in the payload text:")
    for i, block in enumerate(prod_blocks[:10]):
        # Check if it has a title or member count
        title = re.search(r'"title"\s*:\s*"([^"]+)"', block)
        title_str = title.group(1) if title else "No Title"
        m_count = re.search(r'"memberCount"\s*:\s*(\d+)', block)
        m_str = m_count.group(1) if m_count else "None"
        route = re.search(r'"route"\s*:\s*"([^"]+)"', block)
        route_str = route.group(1) if route else "None"
        
        print(f"  Block {i+1}: Route: {route_str} | Title: {title_str} | memberCount: {m_str}")

if __name__ == "__main__":
    main()
