import json
from collections import Counter
import re

def clean_escaped_string(s):
    if not s: return ""
    return s.replace(r'\u0026', '&').replace(r'\u0027', "'").replace('\\"', '"')

def analyze():
    with open(".tmp/reviews_toolsuite.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    low_reviews = data.get("low_reviews", [])
    
    tool_keywords = {
        "pipiads": ["pipiads", "pipi ads", "pipi"],
        "kalodata": ["kalodata", "kalo"],
        "minea": ["minea"],
        "fastmoss": ["fastmoss", "fast moss"],
        "chatgpt": ["chatgpt", "gpt", "gpt-4", "openai"],
        "midjourney": ["midjourney", "mj"],
        "adspy": ["adspy"],
        "helistat": ["helistat"],
        "extension/browser": ["extension", "browser", "chrome", "private browser", "ext"]
    }
    
    tool_mentions = Counter()
    for r in low_reviews:
        desc = (r.get("description") or "").lower()
        for tool, patterns in tool_keywords.items():
            if any(p in desc for p in patterns):
                tool_mentions[tool] += 1
                
    print("Tool Mentions in Low-Star Reviews:")
    for tool, count in tool_mentions.most_common():
        print(f"  {tool}: {count}")
        
    print("\nTotal Low-Star Reviews:", len(low_reviews))
    
    print("\n--- SAMPLE OF LOW-STAR REVIEWS ---")
    for i, r in enumerate(low_reviews[:40]):
        desc = clean_escaped_string(r.get('description', ''))
        print(f"{i+1}. [{r.get('stars')} stars] (User: {r.get('username')}): {desc[:250]}...")

if __name__ == "__main__":
    analyze()
