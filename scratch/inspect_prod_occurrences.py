import requests
import re

def inspect_prod():
    url = "https://whop.com/discover/browse/coaching-and-courses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching page: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        matches = list(re.finditer(r'prod_[a-zA-Z0-9_]+', html))
        print(f"Found {len(matches)} matches of 'prod_...':")
        for i, match in enumerate(matches):
            start = max(0, match.start() - 150)
            end = min(len(html), match.end() + 150)
            print(f"\nMatch {i+1} Context:")
            print(html[start:end].strip())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_prod()
