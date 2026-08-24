import requests
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def parse_categories():
    url = "https://whop.com/sitemaps/categories.xml"
    print(f"Fetching sitemap: {url}...")
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200:
        root = ET.fromstring(resp.content)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('ns:url/ns:loc', ns)
        
        matches = []
        for u in urls:
            loc = u.text
            if any(term in loc.lower() for term in ['ecom', 'commerce', 'drop', 'ship', 'amazon', 'ebay', 'resell', 'retail', 'fba']):
                matches.append(loc)
                
        print(f"Found {len(matches)} relevant category pages matching e-commerce terms:")
        for m in matches[:30]:
            print(f"  - {m}")
            
if __name__ == "__main__":
    parse_categories()
