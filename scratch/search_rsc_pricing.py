import re

def main():
    with open(".tmp/full_rsc_payload.txt", "r", encoding="utf-8") as f:
        payload = f.read()
        
    print(f"Loaded RSC payload of size {len(payload)}")
    
    # 1. Search for plan-like keys in the payload
    keys = ["price", "amount", "plans", "pricing", "billing", "initial_price", "renewal_price"]
    for key in keys:
        matches = [m.start() for m in re.finditer(f'"{key}"', payload)]
        print(f"Found {len(matches)} occurrences of '{key}'")
        for i, pos in enumerate(matches[:5]):
            start = max(0, pos - 100)
            end = min(len(payload), pos + 300)
            print(f"  Occurrence {i+1} at {pos}:")
            print(f"    {payload[start:end]}")
            
    # 2. Search for any plan IDs
    plan_ids = re.findall(r'plan_[a-zA-Z0-9]+', payload)
    print(f"Plan IDs found: {list(set(plan_ids))}")

if __name__ == "__main__":
    main()
