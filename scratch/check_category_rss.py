import requests

def check_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    urls = [
        "https://whop.com/rss/discover/coaching-and-courses.rss",
        "https://whop.com/rss/discover/coaching-and-courses",
        "https://whop.com/rss/discover/trading-and-investing.rss",
        "https://whop.com/discover/browse/coaching-and-courses.rss",
        "https://whop.com/discover/browse/coaching-and-courses/trading-and-investing.rss"
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  [SUCCESS] Found active feed at {url}! Length of response: {len(resp.text)}")
                print(f"  Preview: {resp.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    check_rss()
