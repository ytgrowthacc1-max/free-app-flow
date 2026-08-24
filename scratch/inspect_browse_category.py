import requests
from bs4 import BeautifulSoup
import re
import json

def inspect_category():
    url = "https://whop.com/discover/browse/coaching-and-courses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching category page: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Search for any JSON script tags in the page (e.g., ld+json or NEXT data)
            scripts = soup.find_all('script')
            print(f"Total script tags: {len(scripts)}")
            
            # Let's search for "biz_" or "prod_" in the page source to see if data is inline
            text_content = response.text
            biz_matches = re.findall(r'biz_[a-zA-Z0-9]+', text_content)
            prod_matches = re.findall(r'prod_[a-zA-Z0-9]+', text_content)
            print(f"Occurrences of 'biz_': {len(biz_matches)} (Unique: {len(set(biz_matches))})")
            print(f"Occurrences of 'prod_': {len(prod_matches)} (Unique: {len(set(prod_matches))})")
            
            # Let's print the first few unique business IDs found in the page
            print("Sample unique business IDs found in page:")
            print(list(set(biz_matches))[:10])
            
            # Let's inspect links to see if we can find company slugs directly
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Check for links that go to a community slug (not starting with /discover, /blog, /login, etc.)
                if not href.startswith(('http', 'javascript', '#', '/discover', '/blog', '/login', '/signup', '/careers', '/terms', '/privacy', '/contact', '/about', '/checkout', '/help', '/support', '/sell', '/download', '/pricing', '/dashboard')):
                    if href.strip('/') and '/' not in href.strip('/'):
                        links.append(href.strip('/'))
            
            print(f"\nPotential community slugs from links in DOM (Count: {len(set(links))}):")
            print(list(set(links))[:20])
            
        else:
            print("Failed to fetch category page.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_category()
