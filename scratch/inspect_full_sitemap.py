import requests
from bs4 import BeautifulSoup

def inspect_full_sitemap():
    url = "https://whop.com/sitemap.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching full sitemap: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            
            # Find all sitemap locations (if it's a sitemapindex)
            sitemaps = soup.find_all('sitemap')
            if sitemaps:
                print(f"Found {len(sitemaps)} sitemaps in index:")
                for sm in sitemaps:
                    loc = sm.find('loc')
                    if loc:
                        print(f"  - {loc.text}")
            
            # Find all url locations (if it's a standard urlset)
            urls = soup.find_all('url')
            print(f"Found {len(urls)} URLs directly in sitemap.xml:")
            for i, u in enumerate(urls):
                loc = u.find('loc')
                if loc:
                    print(f"  {i+1:2d}. {loc.text}")
        else:
            print("Failed to fetch sitemap.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_full_sitemap()
