import os
import sys
import json
import time
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "execution"))
from whop_auth import get_fresh_token

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

now = time.time()
cutoff_24h = now - 24 * 3600 # 24 hours ago

print(f"==================================================================", flush=True)
print(f"HIGH-SPEED 24-HOUR FLEET POSTS & VIEW COUNT ANALYZER", flush=True)
print(f"Current Time: {datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
print(f"24h Cutoff:   {datetime.datetime.fromtimestamp(cutoff_24h).strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
print(f"==================================================================\n", flush=True)

# 1. Collect all target channels
targets = []
bot_tokens = {}

for bot_id in sorted(os.listdir(bots_dir)):
    bpath = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bpath):
        continue
    pfile = os.path.join(bpath, "profile.json")
    if not os.path.exists(pfile):
        continue
    try:
        with open(pfile, "r", encoding="utf-8") as f:
            pdata = json.load(f)
    except Exception:
        continue
    
    if pdata.get("suspended") or pdata.get("refresh_token_invalid"):
        continue
    token = pdata.get("oauth_token")
    if not token:
        continue
        
    bot_username = pdata.get("bot_username", bot_id)
    bot_tokens[bot_id] = token
    
    for cname in os.listdir(bpath):
        cpath = os.path.join(bpath, cname)
        if not os.path.isdir(cpath):
            continue
        cfile = os.path.join(cpath, "company.json")
        sfile = os.path.join(cpath, "scheduler_settings.json")
        if os.path.exists(cfile) and os.path.exists(sfile):
            try:
                with open(cfile, "r", encoding="utf-8") as cf:
                    cdata = json.load(cf)
                if not cdata.get("hidden"):
                    exp_id = cdata.get("experience_id")
                    if exp_id:
                        targets.append({
                            "bot_id": bot_id,
                            "bot_username": bot_username,
                            "company_id": cdata.get("company_id", cname),
                            "company_name": cdata.get("company_name", cname),
                            "experience_id": exp_id
                        })
            except Exception:
                pass

print(f"Collected {len(targets)} total active community experience channels across {len(bot_tokens)} bot accounts.", flush=True)

all_posts = []

def fetch_posts_for_channel(t):
    bot_id = t["bot_id"]
    token = bot_tokens.get(bot_id)
    exp_id = t["experience_id"]
    comp_name = t["company_name"]
    bot_username = t["bot_username"]
    
    results = []
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&per=50"
    
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.json()
            items = data if isinstance(data, list) else data.get("data", data.get("posts", []))
            for item in items:
                created_str = item.get("created_at", "")
                created_ts = 0
                if created_str:
                    try:
                        clean_dt = created_str.replace("Z", "+00:00")
                        dt = datetime.datetime.fromisoformat(clean_dt)
                        created_ts = dt.timestamp()
                    except Exception:
                        created_ts = 0

                if created_ts >= cutoff_24h:
                    view_count = item.get("view_count", 0) or 0
                    like_count = item.get("like_count", 0) or 0
                    comment_count = item.get("comment_count", 0) or 0
                    
                    results.append({
                        "id": item.get("id"),
                        "title": item.get("title") or "Untitled Post",
                        "content": (item.get("content") or "")[:200],
                        "bot_username": bot_username,
                        "bot_id": bot_id,
                        "company_name": comp_name,
                        "company_id": t["company_id"],
                        "experience_id": exp_id,
                        "view_count": view_count,
                        "like_count": like_count,
                        "comment_count": comment_count,
                        "created_at": created_str,
                        "created_ts": created_ts,
                        "engagement_score": view_count + (like_count * 2) + (comment_count * 3)
                    })
    except Exception:
        pass
    return results

print("Starting parallel multi-threaded scan (24 workers)...", flush=True)
start_t = time.time()
with ThreadPoolExecutor(max_workers=24) as executor:
    futures = [executor.submit(fetch_posts_for_channel, t) for t in targets]
    for future in as_completed(futures):
        res = future.result()
        if res:
            all_posts.extend(res)

print(f"Scan complete in {time.time() - start_t:.1f}s! Total 24h posts found: {len(all_posts)}", flush=True)

# Deduplicate posts by ID in case any channel was scanned twice
seen_ids = set()
unique_posts = []
for p in all_posts:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        unique_posts.append(p)

all_posts = unique_posts

# Save persistence
out_file = os.path.join(".tmp", "24h_posts_metrics.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(all_posts, f, indent=2)

if not all_posts:
    print("No posts found in the last 24 hours.", flush=True)
    sys.exit(0)

# Aggregation & Analysis
total_views = sum(p["view_count"] for p in all_posts)
total_likes = sum(p["like_count"] for p in all_posts)
total_comments = sum(p["comment_count"] for p in all_posts)
avg_views = total_views / len(all_posts) if all_posts else 0

print(f"\n==================================================================", flush=True)
print(f"24-HOUR AGGREGATE PERFORMANCE METRICS", flush=True)
print(f"==================================================================", flush=True)
print(f"  • Total Unique Posts Analyzed:  {len(all_posts):,}", flush=True)
print(f"  • Total Cumulative Views:       {total_views:,}", flush=True)
print(f"  • Total Likes:                 {total_likes:,}", flush=True)
print(f"  • Total Comments:              {total_comments:,}", flush=True)
print(f"  • Average Views Per Post:      {avg_views:.2f}", flush=True)
print(f"==================================================================\n", flush=True)

# Top 20 Best Performing Posts by View Count
sorted_by_views = sorted(all_posts, key=lambda x: (x["view_count"], x["engagement_score"], x["like_count"]), reverse=True)
print("🏆 TOP 20 BEST PERFORMING POSTS BY VIEW COUNT (LAST 24 HOURS):", flush=True)
print("---------------------------------------------------------------------------------------------------------", flush=True)
for idx, p in enumerate(sorted_by_views[:20], 1):
    print(f"#{idx:02d} | 👁️ {p['view_count']:3d} views | ❤️ {p['like_count']:2d} likes | 💬 {p['comment_count']:2d} comments | Engagement: {p['engagement_score']}", flush=True)
    print(f"     Title: '{p['title']}'", flush=True)
    print(f"     Bot: @{p['bot_username']} | Community: {p['company_name']}", flush=True)
    print(f"     Post ID: {p['id']} | Time: {p['created_at']}", flush=True)
    print("---------------------------------------------------------------------------------------------------------", flush=True)

# Top Performing Communities
comp_stats = {}
for p in all_posts:
    c = p["company_name"]
    if c not in comp_stats:
        comp_stats[c] = {"views": 0, "posts": 0, "likes": 0, "comments": 0}
    comp_stats[c]["views"] += p["view_count"]
    comp_stats[c]["posts"] += 1
    comp_stats[c]["likes"] += p["like_count"]
    comp_stats[c]["comments"] += p["comment_count"]

print("\n📊 TOP 15 COMMUNITIES BY TOTAL VIEW ENGAGEMENT (LAST 24 HOURS):", flush=True)
print("---------------------------------------------------------------------------------------------------------", flush=True)
sorted_comps = sorted(comp_stats.items(), key=lambda x: x[1]["views"], reverse=True)
for idx, (cname, s) in enumerate(sorted_comps[:15], 1):
    avg_cviews = s["views"] / s["posts"] if s["posts"] else 0
    print(f"#{idx:02d} | {cname[:30]:30s} | Views: {s['views']:5d} | Posts: {s['posts']:4d} | Avg: {avg_cviews:.1f} | Likes: {s['likes']:3d} | Comments: {s['comments']:3d}", flush=True)

# Analyze Best Performing Angles / Topics
topic_stats = {}
for p in all_posts:
    # Categorize by title keywords
    t_lower = p["title"].lower()
    cat = "General Discussion"
    if any(k in t_lower for k in ["clearance", "deal", "discount", "price mistake", "penny", "arbitrage", "outlet", "walmart", "target"]):
        cat = "Deal Sourcing & Clearance Arbitrage"
    elif any(k in t_lower for k in ["pick", "parlay", "bet", "odds", "slip", "chalkboard", "line", "sports", "ufc", "nba", "nfl"]):
        cat = "Sports Betting & Daily Picks"
    elif any(k in t_lower for k in ["crypto", "token", "solana", "memecoin", "defi", "trade", "btc", "scalp", "gem"]):
        cat = "Crypto & Token Signals"
    elif any(k in t_lower for k in ["pokemon", "tcg", "card", "charizard", "booster", "grading", "restock", "sniper"]):
        cat = "Pokemon & TCG Reselling"
    elif any(k in t_lower for k in ["saas", "nocode", "app", "software", "tool", "stack", "dev", "micro saas", "builder"]):
        cat = "NoCode Apps & AI SaaS Tools"
    elif any(k in t_lower for k in ["clip", "tiktok", "reels", "shorts", "editor", "video", "capcut", "creator", "bounty"]):
        cat = "Short-Form Video Clipping & Viral Reach"
    elif any(k in t_lower for k in ["retention", "gamifi", "xp", "reward", "streak", "member", "churn", "leaderboard"]):
        cat = "Community Gamification & Member Retention"
    
    if cat not in topic_stats:
        topic_stats[cat] = {"views": 0, "posts": 0, "likes": 0, "comments": 0}
    topic_stats[cat]["views"] += p["view_count"]
    topic_stats[cat]["posts"] += 1
    topic_stats[cat]["likes"] += p["like_count"]
    topic_stats[cat]["comments"] += p["comment_count"]

print("\n🎯 NICHE / TOPIC BREAKDOWN (LAST 24 HOURS):", flush=True)
print("---------------------------------------------------------------------------------------------------------", flush=True)
sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]["views"], reverse=True)
for idx, (cat, s) in enumerate(sorted_topics, 1):
    avg_tviews = s["views"] / s["posts"] if s["posts"] else 0
    print(f"#{idx:02d} | {cat[:45]:45s} | Views: {s['views']:5d} | Posts: {s['posts']:4d} | Avg: {avg_tviews:.1f} | Likes: {s['likes']:3d} | Comments: {s['comments']:3d}", flush=True)
