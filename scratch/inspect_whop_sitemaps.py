import requests
from bs4 import BeautifulSoup

def inspect_sitemaps():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # 1. Newest Arrivals RSS Feed
    rss_url = "https://whop.com/rss/discover/newest_arrivals.rss"
    print(f"Fetching RSS feed: {rss_url}...")
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        print(f"RSS Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            print(f"Found {len(items)} items in RSS feed.")
            if items:
                print("Example item keys/tags:")
                first_item = items[0]
                for tag in first_item.find_all(recursive=False):
                    print(f"  <{tag.name}>: {tag.text[:100]}...")
        else:
            print("Failed to fetch RSS feed.")
    except Exception as e:
        print(f"Error fetching RSS: {e}")

    # 2. Main Sitemap XML
    sitemap_url = "https://whop.com/sitemap.xml"
    print(f"\nFetching Sitemap index: {sitemap_url}...")
    try:
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        print(f"Sitemap Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            sitemaps = soup.find_all('sitemap')
            if sitemaps:
                print(f"Found {len(sitemaps)} sub-sitemaps in the sitemap index:")
                for sm in sitemaps:
                    loc = sm.find('loc')
                    if loc:
                        print(f"  - {loc.text}")
            else:
                urls = soup.find_all('url')
                print(f"Found {len(urls)} URLs directly in this sitemap.")
                for u in urls[:10]:
                    loc = u.find('loc')
                    if loc:
                        print(f"  - {loc.text}")
        else:
            print("Failed to fetch sitemap.")
    except Exception as e:
        print(f"Error fetching sitemap: {e}")

if __name__ == "__main__":
    inspect_sitemaps()
