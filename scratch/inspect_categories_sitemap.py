import requests
from bs4 import BeautifulSoup

def inspect_categories():
    url = "https://whop.com/sitemaps/categories.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching sitemap: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            urls = soup.find_all('url')
            print(f"Found {len(urls)} URLs in this sitemap.")
            
            # Print unique category paths
            paths = []
            for u in urls:
                loc = u.find('loc')
                if loc:
                    paths.append(loc.text)
            
            print("\nExample URLs:")
            for p in paths[:30]:
                print(f"  - {p}")
        else:
            print("Failed to fetch categories sitemap.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_categories()
