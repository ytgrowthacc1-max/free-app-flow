import requests

def main():
    url = "https://whop.com/experiences/exp_KgzMrM89tl4khe/app/posts/post_1Ccw72vtpnGLTJmrtyoxUT?a=bigwlt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    print("Fetching URL:", url)
    r = requests.get(url, headers=headers)
    print("Status code:", r.status_code)
    
    # Save first 50000 chars to check
    html = r.text
    print("Length of HTML:", len(html))
    
    # Let's search for keywords
    keywords = ["ChatGPT", "Grok", "Perplexity", "Leonardo", "Vote", "spending", "option", "poll"]
    for kw in keywords:
        count = html.lower().count(kw.lower())
        print(f"Keyword '{kw}': {count} occurrences")
        
    # Let's search for poll option patterns or print a snippet around "Vote below"
    idx = html.find("Vote below")
    if idx != -1:
        print("\n--- Snippet around 'Vote below' ---")
        print(html[idx-100:idx+500])

if __name__ == "__main__":
    main()
