import requests
import re

def inspect_subcat():
    url = "https://whop.com/discover/browse/coaching-and-courses/trading-and-investing/crypto-trading/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching subcategory: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"HTML size: {len(html)}")
            
            # Search for biz_ and prod_
            biz_ids = set(re.findall(r'biz_[a-zA-Z0-9_]+', html))
            prod_ids = set(re.findall(r'prod_[a-zA-Z0-9_]+', html))
            
            print(f"Found {len(biz_ids)} unique business IDs (biz_...)")
            print(f"Found {len(prod_ids)} unique product IDs (prod_...)")
            
            if biz_ids:
                print("Business IDs:")
                for b in list(biz_ids)[:15]:
                    print(f"  - {b}")
                    
            if prod_ids:
                print("Product IDs:")
                for p in list(prod_ids)[:15]:
                    print(f"  - {p}")
                    
            # Let's search for any external links to find slugs
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                clean = href.replace("https://whop.com", "").strip('/')
                if clean and not clean.startswith((
                    'discover', 'blog', 'login', 'signup', 'careers', 'terms', 'privacy',
                    'contact', 'about', 'checkout', 'help', 'support', 'sell', 'download',
                    'pricing', 'dashboard', 'network', 'home-feed', 'new-business', 'tos', 'search'
                )):
                    if '/' not in clean:
                        links.append((a.text.strip(), clean))
            
            print(f"\nFound {len(set(links))} community links in subcategory page:")
            for text, slug in list(set(links))[:20]:
                print(f"  - {text} ({slug})")
                
        else:
            print("Failed to fetch subcategory page.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_subcat()
