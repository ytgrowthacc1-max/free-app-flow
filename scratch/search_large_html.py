import requests
from bs4 import BeautifulSoup
import re

def search_html():
    url = "https://whop.com/discover/browse/coaching-and-courses/trading-and-investing/crypto-trading/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Print page title
        print(f"Page Title: {soup.title.text if soup.title else 'No Title'}")
        
        # 2. Check for script tags and their sizes
        scripts = soup.find_all('script')
        print(f"\nTotal scripts: {len(scripts)}")
        
        script_sizes = []
        for i, s in enumerate(scripts):
            content = s.string or ""
            if len(content) > 0:
                script_sizes.append((i, len(content), content[:100].strip()))
                
        # Sort by size descending
        script_sizes.sort(key=lambda x: x[1], reverse=True)
        print("\nTop 5 largest script tags:")
        for idx, size, preview in script_sizes[:5]:
            print(f"  Script {idx}: {size} chars - Preview: {preview}")
            # Let's save the largest script to a file to inspect it
            if idx == script_sizes[0][0]:
                with open("scratch/largest_script.js", "w", encoding="utf-8") as f:
                    f.write(scripts[idx].string)
                print(f"    Saved Script {idx} contents to scratch/largest_script.js")
                
        # 3. Search for keyword "crypto" in the largest script
        if script_sizes:
            largest_content = scripts[script_sizes[0][0]].string or ""
            matches = list(re.finditer(r'crypto', largest_content, re.IGNORECASE))
            print(f"\nFound {len(matches)} occurrences of 'crypto' in the largest script tag.")
            for i, match in enumerate(matches[:5]):
                start = max(0, match.start() - 100)
                end = min(len(largest_content), match.end() + 100)
                print(f"  Match {i+1} Context:")
                print(f"    ... {largest_content[start:end].strip()} ...")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_html()
