import os
import sys
import json
import time
import datetime
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "execution"))
from whop_auth import get_fresh_token

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

now = time.time()
cutoff_24h = now - 24 * 3600 # 24 hours ago

print(f"==================================================================")
print(f"SCANNING 24-HOUR POST METRICS & VIEW COUNTS ACROSS ALL ACCOUNTS")
print(f"Current Time: {datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"24h Cutoff:   {datetime.datetime.fromtimestamp(cutoff_24h).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"==================================================================\n")

all_posts = []
scanned_hubs = 0
scanned_bots = 0

# Collect unique active bots and their experiences
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
    if not pdata.get("oauth_token"):
        continue
        
    bot_username = pdata.get("bot_username", bot_id)
    
    # Get all active companies under this bot
    active_companies = []
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
                with open(sfile, "r", encoding="utf-8") as sf:
                    sdata = json.load(sf)
                if not cdata.get("hidden"):
                    exp_id = sdata.get("experience_id") or cdata.get("experience_id")
                    if exp_id:
                        active_companies.append({
                            "company_id": cdata.get("company_id", cname),
                            "company_name": cdata.get("company_name", cname),
                            "experience_id": exp_id,
                            "is_master": sdata.get("master_switch_enabled", True) and (sdata.get("scheduler_enabled") or sdata.get("autopilot_enabled"))
                        })
            except Exception:
                pass

    if not active_companies:
        continue

    # Get valid token for this bot
    token = None
    try:
        token = get_fresh_token(bot_id, prevent_auto_auth=True)
    except Exception:
        token = pdata.get("oauth_token")

    if not token:
        continue

    scanned_bots += 1
    headers = {"Authorization": f"Bearer {token}"}

    for comp in active_companies:
        exp_id = comp["experience_id"]
        comp_name = comp["company_name"]
        scanned_hubs += 1

        try:
            url = f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&per=50"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                raw_data = resp.json()
                items = raw_data if isinstance(raw_data, list) else raw_data.get("data", raw_data.get("posts", []))
                
                for item in items:
                    # Parse created_at ISO format
                    created_str = item.get("created_at", "")
                    created_ts = 0
                    if created_str:
                        try:
                            # Handle ISO format like 2026-08-23T02:04:52.749Z
                            clean_dt = created_str.replace("Z", "+00:00")
                            dt = datetime.datetime.fromisoformat(clean_dt)
                            created_ts = dt.timestamp()
                        except Exception:
                            created_ts = 0

                    # Filter last 24h
                    if created_ts >= cutoff_24h:
                        view_count = item.get("view_count", 0) or 0
                        like_count = item.get("like_count", 0) or 0
                        comment_count = item.get("comment_count", 0) or 0
                        
                        all_posts.append({
                            "id": item.get("id"),
                            "title": item.get("title") or "Untitled Post",
                            "content": (item.get("content") or "")[:200],
                            "bot_username": bot_username,
                            "bot_id": bot_id,
                            "company_name": comp_name,
                            "company_id": comp["company_id"],
                            "experience_id": exp_id,
                            "view_count": view_count,
                            "like_count": like_count,
                            "comment_count": comment_count,
                            "created_at": created_str,
                            "created_ts": created_ts,
                            "engagement_score": view_count + (like_count * 2) + (comment_count * 3)
                        })
            else:
                pass
        except Exception as e:
            pass

        time.sleep(0.05) # fast scan

print(f"Scanned {scanned_bots} bots across {scanned_hubs} community experience channels.")
print(f"Total posts found published in the last 24 hours: {len(all_posts)}")

# Save raw collected metrics for persistence
out_file = os.path.join(".tmp", "24h_posts_metrics.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(all_posts, f, indent=2)

if not all_posts:
    print("No posts found in the last 24 hours.")
    sys.exit(0)

# Aggregation & Analysis
total_views = sum(p["view_count"] for p in all_posts)
total_likes = sum(p["like_count"] for p in all_posts)
total_comments = sum(p["comment_count"] for p in all_posts)
avg_views = total_views / len(all_posts) if all_posts else 0

print(f"\n==================================================================")
print(f"24-HOUR AGGREGATE PERFORMANCE METRICS")
print(f"==================================================================")
print(f"  • Total Posts Analyzed:        {len(all_posts):,}")
print(f"  • Total Cumulative Views:       {total_views:,}")
print(f"  • Total Likes:                 {total_likes:,}")
print(f"  • Total Comments:              {total_comments:,}")
print(f"  • Average Views Per Post:      {avg_views:.2f}")
print(f"==================================================================\n")

# Top 15 Best Performing Posts by View Count
sorted_by_views = sorted(all_posts, key=lambda x: (x["view_count"], x["engagement_score"]), reverse=True)
print("🏆 TOP 15 BEST PERFORMING POSTS BY VIEW COUNT (LAST 24 HOURS):")
print("---------------------------------------------------------------------------------------------------------")
for idx, p in enumerate(sorted_by_views[:15], 1):
    print(f"#{idx:02d} | 👁️ {p['view_count']:3d} views | ❤️ {p['like_count']:2d} likes | 💬 {p['comment_count']:2d} comments | Score: {p['engagement_score']}")
    print(f"     Title: '{p['title']}'")
    print(f"     Bot: @{p['bot_username']} | Community: {p['company_name']}")
    print(f"     Post ID: {p['id']} | Time: {p['created_at']}")
    print("---------------------------------------------------------------------------------------------------------")

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

print("\n📊 TOP 10 COMMUNITIES BY TOTAL VIEW ENGAGEMENT (LAST 24 HOURS):")
print("---------------------------------------------------------------------------------------------------------")
sorted_comps = sorted(comp_stats.items(), key=lambda x: x[1]["views"], reverse=True)
for idx, (cname, s) in enumerate(sorted_comps[:10], 1):
    avg_cviews = s["views"] / s["posts"] if s["posts"] else 0
    print(f"#{idx:02d} | {cname[:30]:30s} | Total Views: {s['views']:4d} | Posts: {s['posts']:3d} | Avg Views: {avg_cviews:.1f} | Likes: {s['likes']:2d} | Comments: {s['comments']:2d}")
