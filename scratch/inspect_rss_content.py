import requests

def inspect_content():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    urls = {
        "newest_arrivals": "https://whop.com/rss/discover/newest_arrivals.rss",
        "coaching_courses_rss": "https://whop.com/rss/discover/coaching-and-courses.rss",
        "categories_sitemap": "https://whop.com/sitemaps/categories.xml"
    }
    
    for name, url in urls.items():
        print(f"\n--- URL: {name} ({url}) ---")
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            print(f"  Status Code: {resp.status_code}")
            print(f"  Content-Type: {resp.headers.get('Content-Type')}")
            print(f"  Preview: {resp.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    inspect_content()
