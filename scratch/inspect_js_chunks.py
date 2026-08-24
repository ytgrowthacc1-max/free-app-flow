import requests
from bs4 import BeautifulSoup
import re

def inspect_chunks():
    url = "https://whop.com/discover"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching discover page to find JS chunk URLs...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all chunk URLs
        chunk_urls = []
        for s in soup.find_all('script', src=True):
            src = s['src']
            if '/_next/static/chunks/' in src:
                if src.startswith('/'):
                    chunk_urls.append("https://whop.com" + src)
                else:
                    chunk_urls.append(src)
                    
        print(f"Found {len(chunk_urls)} Next.js chunk scripts.")
        
        # Fetch and search chunks
        # We will look for search clients, endpoints, or keys
        patterns = [
            r'https?://[a-zA-Z0-9\-\.]+\.algolia\.net',
            r'https?://[a-zA-Z0-9\-\.]+\.algolianet\.com',
            r'/api/v[0-9]+/discover',
            r'/api/v[0-9]+/search',
            r'algolia',
            r'typesense',
            r'meilisearch',
            r'https?://api\.whop\.com/api/[a-zA-Z0-9_/]+'
        ]
        
        found_matches = {}
        for idx, chunk_url in enumerate(chunk_urls[:40]): # Check first 40 chunks
            print(f"  Fetching chunk {idx+1}/{len(chunk_urls)}: {chunk_url.split('/')[-1].split('?')[0]}")
            try:
                chunk_resp = requests.get(chunk_url, headers=headers, timeout=5)
                if chunk_resp.status_code == 200:
                    text = chunk_resp.text
                    for p in patterns:
                        matches = re.findall(p, text, re.IGNORECASE)
                        if matches:
                            if p not in found_matches:
                                found_matches[p] = []
                            found_matches[p].extend(matches)
                            print(f"    -> Found matches for pattern '{p}': {list(set(matches))[:5]}")
                            # Print a bit of context
                            first_match = re.search(p, text, re.IGNORECASE)
                            if first_match:
                                start = max(0, first_match.start() - 100)
                                end = min(len(text), first_match.end() + 100)
                                print(f"       Context: ... {text[start:end].strip()} ...")
            except Exception as e:
                print(f"    Error fetching chunk: {e}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_chunks()
