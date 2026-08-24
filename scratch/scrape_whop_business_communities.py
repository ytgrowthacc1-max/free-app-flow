import os
import sys
import json
import logging
import requests
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure UTF-8 printing on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

ALGOLIA_APP_ID = "QLKQ4FZ8HM"
ALGOLIA_API_KEY = "edc79c87d243ec3b7368aafae5ea54db"
ALGOLIA_INDEX = "production_products"

# Comprehensive list of search terms targeting business owners, community owners, and advertisers
SEARCH_TERMS = [
    # Whop/Platform Specific
    "whop ads", "whop growth", "community growth", "whop guide",
    # Paid Ads & Marketing
    "facebook ads", "tiktok ads", "google ads", "media buying", "ads mastery", "paid traffic",
    # E-commerce & Dropshipping
    "dropshipping", "ecommerce", "shopify", "amazon fba", "wholesale", "private label", "ebay reselling",
    # Agency & Service
    "smma", "marketing agency", "agency building", "appointment setting", "high ticket sales", "sales closing",
    # Outreach & Lead Gen
    "cold email", "lead generation", "outreach", "cold outreach", "copywriting", "funnel building",
    # Creators & Content
    "youtube automation", "content creator", "tiktok shop", "ugc", "video editing", "clipping",
    # Software & SaaS
    "saas", "nocode", "no-code", "bubble.io", "webflow", "ai agents", "automation", "discord bot",
    # Reselling & Arbitrage
    "reselling", "retail arbitrage", "cook group", "ticket reselling", "sneaker bot", "deal group",
    # General Business & Growth
    "business strategy", "marketing strategy", "make money online", "monetize"
]

# Industry types to filter directly in Algolia
INDUSTRY_TYPES = [
    "business_strategy",
    "make_money_online_community",
    "reselling_community",
    "digital_product_creation",
    "content_creator_community",
    "agency_building",
    "web_development_agency",
    "dropshipping_coaching",
    "digital_marketing",
    "ecommerce_education",
    "smma",
    "retail_arbitrage",
    "youtube_automation",
    "ai_business_community",
    "ai_automation_agency",
    "content_business_community",
    "instagram_growth",
    "workflow_automation_software",
    "ai_agent_building",
    "performance_marketing_agency",
    "coaching_business_coaching",
    "resale_arbitrage_tool",
    "niche_service",
    "social_media"
]

def clean_text(text):
    if not text:
        return ""
    return " ".join(str(text).split())

def query_algolia_by_term(query_str):
    url = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"
    headers = {
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "X-Algolia-API-Key": ALGOLIA_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "params": f"query={requests.utils.quote(query_str)}&hitsPerPage=250&filters=marketplace_status:live_marketplace"
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json().get("hits", [])
    except Exception as e:
        log.error(f"Algolia query failed for term '{query_str}': {e}")
        return []

def query_algolia_by_industry(industry_type):
    url = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"
    headers = {
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "X-Algolia-API-Key": ALGOLIA_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "params": f"filters=marketplace_status:live_marketplace AND industry_type:{industry_type}&hitsPerPage=250"
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json().get("hits", [])
    except Exception as e:
        log.error(f"Algolia query failed for industry '{industry_type}': {e}")
        return []

def fetch_company_details(h):
    bot_tag = h.get("bot_tag")
    bot_name = h.get("bot_name") or h.get("title")
    product_route = h.get("route")
    
    if not bot_tag:
        return None
        
    comp_url = f"https://api.whop.com/api/v1/companies/{bot_tag}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = requests.get(comp_url, headers=headers, timeout=8)
            
            if res.status_code == 200:
                cdata = res.json()
                reviews_count = cdata.get("published_reviews_count", 0)
                member_count = cdata.get("member_count", 0)
                route = cdata.get("route")
                title = clean_text(cdata.get("title") or bot_name or "Untitled")
                desc = clean_text(cdata.get("description") or cdata.get("target_audience") or h.get("shortened_description") or "")
                
                # We only want groups with >= 1000 members
                if not member_count or member_count < 1000:
                    return None
                    
                if route:
                    link = f"https://whop.com/{route}"
                else:
                    link = f"https://whop.com/discover/{product_route}" if product_route else ""
                    
                social_links = cdata.get("social_links", [])
                socials_str = "; ".join([f"{s.get('website')}:{s.get('url')}" for s in social_links if s.get('url')])
                
                reasoning = generate_reasoning(title, desc, h.get("industry_type", ""))
                
                return {
                    "name": title,
                    "link": link,
                    "bot_tag": bot_tag,
                    "reviews": reviews_count,
                    "members": member_count,
                    "industry_type": h.get("industry_type", "unknown"),
                    "socials": socials_str,
                    "description": desc,
                    "reasoning": reasoning
                }
            elif res.status_code == 429:
                time.sleep(2)
                continue
            else:
                break
        except Exception as e:
            time.sleep(1)
            
    return None

def generate_reasoning(title, desc, industry_type):
    t_lower = title.lower()
    d_lower = desc.lower()
    ind_lower = str(industry_type).lower()
    
    if "whop ads" in t_lower or "whop ads" in d_lower or "whop growth" in t_lower or "whop growth" in d_lower:
        return "Whop growth/ads group. Members here are Whop community owners actively looking to run ads, promote, and scale their Whop groups. They are prime targets who already sell digital products on the platform."
        
    elif any(x in t_lower or x in d_lower for x in ["facebook ads", "tiktok ads", "google ads", "media buying", "ads mastery", "media buy"]):
        return "Paid advertising/media buying community. Members are business owners, media buyers, and marketers looking to scale paid campaigns, meaning they have products or services to promote and active marketing budgets."
        
    elif any(x in t_lower or x in d_lower for x in ["dropship", "shopify", "ecom", "amazon fba", "retail arbitrage", "wholesale", "private label"]):
        return "E-commerce/dropshipping mastermind. Members are e-commerce business owners who manage digital stores, run ads, and scale online operations, representing active online sellers with scaling needs."
        
    elif any(x in t_lower or x in d_lower for x in ["smma", "marketing agency", "agency building", "cold email", "lead generation", "appointment setting", "outreach"]):
        return "Agency building/client acquisition group. Members are agency owners, freelancers, and service providers seeking client outreach strategies, funnel building, and business operations scaling."
        
    elif any(x in t_lower or x in d_lower for x in ["saas", "nocode", "no-code", "bubble.io", "webflow", "software"]):
        return "Software/SaaS development group. Members are software founders and developers building digital platforms, looking to scale their software products and acquire users."
        
    elif any(x in t_lower or x in d_lower for x in ["youtube automation", "content creator", "tiktok shop", "ugc", "video editing", "clipping"]):
        return "Content monetization/creator economy. Members are video editors, channel owners, and creators building digital media assets, looking to scale traffic, build audiences, and monetize views."
        
    elif any(x in t_lower or x in d_lower for x in ["reselling", "cook group", "ticket reselling", "sneaker bot", "deal group"]):
        return "Reselling/deal arbitrage community. Members run micro-reselling businesses, sourcing inventory and automating sales. The owners and members manage high-volume online transacting businesses."
        
    elif any(x in t_lower or x in d_lower for x in ["copywriting", "sales closing", "high ticket"]):
        return "Sales/copywriting training. Members are professional copywriters, closers, or sales reps helping other businesses write landing pages, run campaigns, and scale sales conversion."
        
    # Default fallback reasonings based on industry types
    if "marketing" in ind_lower or "agency" in ind_lower:
        return "Digital marketing/agency community. Members are service business owners and marketers focused on client acquisition, funnel optimization, and scaling client work."
    elif "ecom" in ind_lower or "dropshipping" in ind_lower:
        return "E-commerce business group. Members are brand builders and online retailers sourcing inventory and learning advertising to scale storefront sales."
    elif "reselling" in ind_lower or "arbitrage" in ind_lower:
        return "Reselling community. Members run independent reselling businesses, flips, and deal sourcing. They rely heavily on botting, tools, and advertising to scale sales."
    elif "make_money_online" in ind_lower or "business_strategy" in ind_lower:
        return "General business strategy and monetization group. Members are entrepreneurs starting or growing online ventures, seeking networking and strategies to launch and promote their products."
    else:
        return "Active digital entrepreneurship group. Members are online business owners, freelancers, and side-hustlers focused on growth strategies, automation, and scaling their income streams."

def main():
    log.info("Starting Whop business/marketing community search for groups with >= 1000 members...")
    
    all_hits = []
    seen_tags = set()
    
    # 1. Search Algolia for all terms
    log.info(f"Querying Algolia index for {len(SEARCH_TERMS)} keywords...")
    for term in SEARCH_TERMS:
        hits = query_algolia_by_term(term)
        for h in hits:
            bot_tag = h.get("bot_tag")
            if bot_tag and bot_tag not in seen_tags:
                seen_tags.add(bot_tag)
                all_hits.append(h)
                
    log.info(f"Unique communities found via keywords: {len(all_hits)}")
    
    # 2. Search Algolia for all industry types
    log.info(f"Querying Algolia index for {len(INDUSTRY_TYPES)} industry types...")
    for ind in INDUSTRY_TYPES:
        hits = query_algolia_by_industry(ind)
        for h in hits:
            bot_tag = h.get("bot_tag")
            if bot_tag and bot_tag not in seen_tags:
                seen_tags.add(bot_tag)
                all_hits.append(h)
                
    log.info(f"Total unique communities found: {len(all_hits)}")
    
    # Pre-filtering: Filter out sport picks or betting from search terms to ensure relevance
    exclude_keywords = ["betting", "picks", "signals", "sportsbook", "sports betting", "femboy"]
    filtered_hits = []
    for h in all_hits:
        title = clean_text(h.get("title") or h.get("bot_name") or "").lower()
        desc = clean_text(h.get("shortened_description") or "").lower()
        headline = clean_text(h.get("headline") or "").lower()
        
        has_exclude = any(kw in title or kw in desc or kw in headline for kw in exclude_keywords)
        if has_exclude and not any(k in title or k in desc for k in ["agency", "coaching", "business", "growth"]):
            continue
            
        filtered_hits.append(h)
        
    log.info(f"Filtered down to {len(filtered_hits)} highly relevant potential business/marketing/growth communities.")
    
    # Process hits in parallel chunks of 200 to find at least 60-70 target communities
    chunk_size = 200
    leads = []
    target_count = 65
    
    log.info("Fetching details and member counts from Whop API in parallel chunks...")
    for i in range(0, len(filtered_hits), chunk_size):
        chunk = filtered_hits[i:i+chunk_size]
        log.info(f"Processing chunk {i//chunk_size + 1} (size {len(chunk)})...")
        
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = {executor.submit(fetch_company_details, h): h for h in chunk}
            for future in as_completed(futures):
                try:
                    res = future.result()
                    if res:
                        leads.append(res)
                except Exception as e:
                    log.error(f"Thread execution error: {e}")
                    
        log.info(f"Currently found {len(leads)} communities with >= 1000 members.")
        if len(leads) >= target_count:
            log.info(f"Reached target count ({target_count}). Stopping search.")
            break
            
        time.sleep(2)
        
    # Sort leads by reviews count (high activity) and then member count
    leads.sort(key=lambda x: (x["members"], x["reviews"]), reverse=True)
    
    log.info(f"Total big business communities found and writing to CSV: {len(leads)}")
    
    # Save to CSV
    output_csv = "scratch/whop_business_communities.csv"
    fields = ["Community Name", "Community Link", "Members Count", "Reviews Count", "Community Description", "Reasoning Behind Choice", "Industry Type", "Social Links"]
    
    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        
        for l in leads:
            writer.writerow([
                l["name"],
                l["link"],
                l["members"],
                l["reviews"],
                l["description"],
                l["reasoning"],
                l["industry_type"],
                l["socials"]
            ])
            
    log.info(f"Saved results to CSV: {output_csv}")
    
    # Output first 10 for review
    log.info("\nFirst 10 communities:")
    for idx, l in enumerate(leads[:10]):
        log.info(f"{idx+1}. {l['name']} | Members: {l['members']} | Link: {l['link']}")
        log.info(f"   Reasoning: {l['reasoning']}")
        log.info("-" * 40)

if __name__ == "__main__":
    main()
