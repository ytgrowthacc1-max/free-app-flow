import requests
import json
from bs4 import BeautifulSoup

def inspect_community():
    url = "https://whop.com/h2o-calm-academy/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching community page: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Look for JSON-LD structured data (rich snippets)
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            print(f"\nFound {len(json_ld_scripts)} type='application/ld+json' scripts:")
            for i, script in enumerate(json_ld_scripts):
                try:
                    js_data = json.loads(script.string)
                    print(f"  LD-JSON {i} Type: {js_data.get('@type') or js_data.get('@context')}")
                    # Write to files for inspection
                    with open(f"scratch/ld_json_{i}.json", "w", encoding="utf-8") as f:
                        json.dump(js_data, f, indent=2)
                except Exception as e:
                    print(f"  Failed to parse script {i}: {e}")
                    
            # 2. Look for OpenGraph and twitter meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
                    
            print("\nKey Meta Tags:")
            for k in ['og:title', 'og:description', 'og:image', 'og:url', 'twitter:title', 'twitter:description', 'keywords']:
                if k in meta_tags:
                    print(f"  {k}: {meta_tags[k]}")
                    
            # Save all meta tags to a file
            with open("scratch/meta_tags.json", "w", encoding="utf-8") as f:
                json.dump(meta_tags, f, indent=2)
                
            # 3. Look for elements containing social links (Twitter, Instagram, Discord, YouTube, Telegram)
            social_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                for domain in ['twitter.com', 'x.com', 'instagram.com', 'discord.gg', 'discord.com', 'youtube.com', 't.me', 'telegram.me']:
                    if domain in href:
                        social_links.append(href)
            social_links = list(set(social_links))
            print(f"\nFound {len(social_links)} potential social links:")
            for link in social_links:
                print(f"  - {link}")
                
            # 4. Look for links containing app store or experience information
            experience_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/exp_' in href or '/app_' in href:
                    experience_links.append(href)
            print(f"Found {len(experience_links)} experience/app links in the DOM.")
            
        else:
            print("Failed to fetch community page.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_community()
