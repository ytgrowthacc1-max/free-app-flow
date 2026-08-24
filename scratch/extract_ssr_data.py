import json
import re

def main():
    with open("c:/Python/WHOP AUTOMATION AGENTIC/scratch/fetch_page_html.py", "r") as f:
        pass # just checking files
        
    import requests
    url = "https://whop.com/experiences/exp_KgzMrM89tl4khe/app/posts/post_1Ccw72vtpnGLTJmrtyoxUT?a=bigwlt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    html = r.text
    
    # Let's find script tags containing json data
    # Whop might use Next.js, search for __NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if match:
        print("[SUCCESS] Found __NEXT_DATA__ script tag!")
        data = json.loads(match.group(1))
        # Save to a file so we can view/search it
        with open("scratch/next_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("Saved next_data.json.")
        return
        
    # Search for other JSON-like variables inside script tags
    matches = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(matches)} generic script tags.")
    for idx, content in enumerate(matches):
        if "post_" in content or "exp_" in content:
            print(f"Script tag {idx} contains post/exp reference. Length: {len(content)}")
            # Try to extract JSON strings
            json_matches = re.findall(r'(\{.*?\})', content)
            print(f"  Found {len(json_matches)} potential JSON blocks.")
            
    # Also search for any JSON-like data using regex
    # Next.js 13+ App Router often uses self-hydration chunks like: self.__next_f.push([1, "JSON"])
    next_f_chunks = re.findall(r'self\.__next_f\.push\(\[1,\s*"(.*?)"\]\)', html)
    if next_f_chunks:
        print(f"[SUCCESS] Found {len(next_f_chunks)} self.__next_f.push chunks!")
        # Reconstruct next_f content
        full_text = ""
        for chunk in next_f_chunks:
            # Decode escaped characters
            decoded = chunk.replace('\\"', '"').replace('\\\\', '\\')
            full_text += decoded
            
        with open("scratch/next_f_data.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
        print("Saved next_f_data.txt.")
        
        # Search for post ID or poll
        for line in full_text.splitlines():
            if "post_1Ccw72vtpnGLTJmrtyoxUT" in line or "poll" in line:
                print("  Matching chunk line snippet:")
                print(line[:200])

if __name__ == "__main__":
    main()
