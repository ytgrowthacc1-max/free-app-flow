import requests
from bs4 import BeautifulSoup

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = "https://whop.com/tpai/"
    resp = requests.get(url, headers=headers)
    print(f"Status Code: {resp.status_code}")
    print(f"Length of HTML: {len(resp.text)}")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Print script tags
    scripts = soup.find_all('script')
    print(f"Total script tags found: {len(scripts)}")
    for i, s in enumerate(scripts):
        attrs = s.attrs
        src = attrs.get('src', '')
        sid = attrs.get('id', '')
        stype = attrs.get('type', '')
        snippet = s.string[:60].replace('\n', ' ') if s.string else ''
        print(f"  Script {i}: ID='{sid}' Src='{src}' Type='{stype}' Content='{snippet}...'")

if __name__ == "__main__":
    main()
