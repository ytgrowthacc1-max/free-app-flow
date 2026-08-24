import requests
from bs4 import BeautifulSoup

def inspect_html_sitemap():
    url = "https://whop.com/sitemap"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching HTML Sitemap: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links on the page
            links = soup.find_all('a', href=True)
            print(f"Found {len(links)} total links on the page.")
            
            # Filter links that represent communities (not standard company pages, login, blog, etc.)
            community_links = []
            for a in links:
                href = a['href']
                text = a.text.strip()
                
                # Check if it goes to a community (usually a clean path /slug/ or whop.com/slug/)
                # Let's filter out known static page prefixes
                clean_href = href.replace("https://whop.com", "").strip('/')
                
                if clean_href and not clean_href.startswith((
                    'discover', 'blog', 'login', 'signup', 'careers', 'terms', 'privacy',
                    'contact', 'about', 'checkout', 'help', 'support', 'sell', 'download',
                    'pricing', 'dashboard', 'network', 'home-feed', 'new-business', 'tos', 'search'
                )):
                    if '/' not in clean_href:  # Just a single slug
                        community_links.append((text, clean_href))
                        
            print(f"\nPotential community links in sitemap (Count: {len(set(community_links))}):")
            for text, slug in list(set(community_links))[:30]:
                print(f"  - {text} ({slug})")
                
            # Let's write the parsed community links to a JSON file for analysis
            output_data = [{"name": name, "slug": slug} for name, slug in list(set(community_links))]
            with open("scratch/html_sitemap_communities.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2)
            print(f"\nSaved parsed community list to scratch/html_sitemap_communities.json")
            
        else:
            print("Failed to fetch HTML sitemap.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_html_sitemap()
