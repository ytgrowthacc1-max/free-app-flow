import requests
import re

def inspect_chunk_14():
    # Let's find the script URL dynamically by searching the page
    url = "https://whop.com/discover"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print("Finding Chunk 14 URL...")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        chunk_url = None
        for s in soup.find_all('script', src=True):
            src = s['src']
            if '0k0sfs1bz5f-o.js' in src:
                chunk_url = "https://whop.com" + src if src.startswith('/') else src
                break
                
        if not chunk_url:
            print("Could not find the exact chunk 14 script in HTML. Using static check.")
            # Fallback to search list of all scripts for the pattern
            for s in soup.find_all('script', src=True):
                if 'chunks/' in s['src']:
                    src = "https://whop.com" + s['src'] if s['src'].startswith('/') else s['src']
                    chunk_text = requests.get(src, headers=headers).text
                    if "QLKQ4FZ8HM" in chunk_text:
                        chunk_url = src
                        print(f"Found QLKQ4FZ8HM in chunk: {chunk_url}")
                        break
                        
        if not chunk_url:
            print("[ERROR] Could not find chunk containing Algolia App ID")
            return
            
        print(f"Fetching chunk from: {chunk_url}")
        js_content = requests.get(chunk_url, headers=headers).text
        
        # Search for QLKQ4FZ8HM
        print("\nSearching for QLKQ4FZ8HM context:")
        matches = list(re.finditer("QLKQ4FZ8HM", js_content))
        for m in matches:
            start = max(0, m.start() - 300)
            end = min(len(js_content), m.end() + 300)
            print(f"--- Context ---")
            print(js_content[start:end].strip())
            
        # Search for NEXT_PUBLIC_ALGOLIA
        print("\nSearching for NEXT_PUBLIC_ALGOLIA context:")
        matches_alg = list(re.finditer("NEXT_PUBLIC_ALGOLIA", js_content))
        for m in matches_alg:
            start = max(0, m.start() - 150)
            end = min(len(js_content), m.end() + 150)
            print(f"--- Algolia Context ---")
            print(js_content[start:end].strip())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_chunk_14()
