import requests
import re

def search_keywords():
    url = "https://whop.com/discover/browse/coaching-and-courses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        keywords = ["algolia", "applicationId", "apiKey", "indexName", "typesense", "meilisearch", "search", "graphql", "apollo", "urql", "client"]
        
        print("\nKeyword check in page HTML:")
        for kw in keywords:
            matches = list(re.finditer(kw, html, re.IGNORECASE))
            print(f"  Keyword '{kw}': {len(matches)} occurrences")
            if len(matches) > 0 and kw in ["algolia", "typesense", "meilisearch", "indexName", "applicationId"]:
                # Print context around matches
                for match in matches[:3]:
                    start = max(0, match.start() - 100)
                    end = min(len(html), match.end() + 100)
                    print(f"    Context: ... {html[start:end].strip()} ...")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_keywords()
