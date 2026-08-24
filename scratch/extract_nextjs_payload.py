import requests
import re
from bs4 import BeautifulSoup

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = "https://whop.com/tpai/"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch page: {resp.status_code}")
        return
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Collect all script content that starts with self.__next_f.push
    rsc_parts = []
    for script in soup.find_all('script'):
        if script.string and 'self.__next_f.push' in script.string:
            # Extract the string inside push
            # Format: self.__next_f.push([1,"CONTENT"]) or self.__next_f.push([1,"CONTENT\n"])
            matches = re.findall(r'self\.__next_f\.push\(\[1,\s*"(.*?)"\s*\]\)', script.string, re.DOTALL)
            for m in matches:
                # Unescape some common escapes like \", \\, \n
                clean = m.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
                rsc_parts.append(clean)
                
    full_rsc = "\n".join(rsc_parts)
    print(f"Total RSC content length: {len(full_rsc)}")
    
    # Save the full RSC payload to a file for analysis
    with open(".tmp/full_rsc_payload.txt", "w", encoding="utf-8") as f:
        f.write(full_rsc)
        
    # Search for product IDs in the RSC payload and print the surrounding 300 characters
    product_ids = [
        "prod_idrEecSloni51", # HEXR PRO
        "prod_T6Icayc7fXnLF", # TRADINGPILOTAI
        "prod_vh0ZNaCvmLmKZ"  # VIP Discord Access
    ]
    
    for pid in product_ids:
        print("\n" + "="*80)
        print(f"Searching for occurrences of {pid} in RSC payload:")
        
        matches = [m.start() for m in re.finditer(pid, full_rsc)]
        if not matches:
            print("  Not found in self.__next_f.push payload directly.")
            continue
            
        for idx, pos in enumerate(matches):
            start = max(0, pos - 100)
            end = min(len(full_rsc), pos + 400)
            snippet = full_rsc[start:end]
            print(f"\n  Occurrence {idx + 1} (pos {pos}):")
            print(snippet)
            
            # Use regex to find prices or dollar signs in the snippet
            prices_in_snippet = re.findall(r'\$\d+(?:\.\d{2})?|\b\d+(?:\.\d{2})?\b\s*(?:USD|EUR)', snippet)
            print(f"  Possible pricing terms in snippet: {prices_in_snippet}")
        print("="*80)

if __name__ == "__main__":
    main()
