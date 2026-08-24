import re

def main():
    with open(".tmp/full_rsc_payload.txt", "r", encoding="utf-8") as f:
        payload = f.read()
        
    slugs = [
        "ai-trading-vip",
        "hexr-pro-41",
        "vip-tradingpilotai-discord-access"
    ]
    
    for slug in slugs:
        print("\n" + "="*90)
        print(f"Searching for '{slug}' in RSC payload:")
        matches = [m.start() for m in re.finditer(slug, payload)]
        if not matches:
            print("  No matches found.")
            continue
            
        for i, pos in enumerate(matches):
            start = max(0, pos - 100)
            end = min(len(payload), pos + 1200)
            snippet = payload[start:end]
            print(f"\n  Match {i+1} at index {pos}:")
            print(snippet)
        print("="*90)

if __name__ == "__main__":
    main()
