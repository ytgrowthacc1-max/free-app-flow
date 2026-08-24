import requests
import re
import json

def parse_rsc():
    url = "https://whop.com/discover/browse/coaching-and-courses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching page: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        print(f"HTML Page size: {len(html)} characters")
        
        # Extract all script tags containing self.__next_f.push
        # Pattern matches self.__next_f.push(something)
        pattern = r'self\.__next_f\.push\(\[(.*?)\].*?\)'
        matches = re.findall(pattern, html, re.DOTALL)
        print(f"Found {len(matches)} matches of self.__next_f.push(...)")
        
        # Let's write out all extracted RSC chunks to a file to inspect
        rsc_text = ""
        for i, match in enumerate(matches):
            rsc_text += f"\n--- CHUNK {i} ---\n{match}\n"
            
        with open("scratch/rsc_payload_chunks.txt", "w", encoding="utf-8") as f:
            f.write(rsc_text)
            
        print("Wrote raw RSC chunks to scratch/rsc_payload_chunks.txt")
        
        # Let's search for patterns:
        # 1. Product IDs: prod_...
        # 2. Company IDs: biz_...
        # 3. Slugs: check if there are links to products or companies
        
        # We can extract all quoted strings in the RSC chunks
        # Let's search for "biz_" and "prod_" specifically in the raw HTML again
        # to see if they exist anywhere (case sensitive)
        all_biz = re.findall(r'biz_[a-zA-Z0-9_]+', html)
        all_prod = re.findall(r'prod_[a-zA-Z0-9_]+', html)
        
        print(f"Total occurrences of 'biz_' in raw HTML: {len(all_biz)}")
        print(f"Total occurrences of 'prod_' in raw HTML: {len(all_prod)}")
        
        # Let's search for usernames or slugs. For example, "whop" or "ecomtalent"
        for slug in ["whop", "ecomtalent", "app-builders", "h2o-calm-academy"]:
            matches_slug = re.findall(slug, html, re.IGNORECASE)
            print(f"Occurrences of '{slug}': {len(matches_slug)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_rsc()
