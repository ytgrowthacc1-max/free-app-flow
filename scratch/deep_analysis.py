import json
import datetime
from collections import defaultdict
import re

# Load raw posts
with open(r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\analyzed_posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} posts for deep analysis.")

# 1. Posting Time Analysis (Hour of day and Day of week in EDT/UTC-4)
hour_stats = defaultdict(lambda: {"views": 0, "likes": 0, "comments": 0, "count": 0})
day_stats = defaultdict(lambda: {"views": 0, "likes": 0, "comments": 0, "count": 0})

def get_day_name(val):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[val]

for p in posts:
    created_at = p.get("created_at")
    if not created_at:
        continue
    try:
        dt = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except:
        continue
    
    # Convert to EDT (UTC-4)
    edt_dt = dt - datetime.timedelta(hours=4)
    edt_hour = edt_dt.hour
    edt_day = edt_dt.weekday()
    
    hour_stats[edt_hour]["views"] += p["views"]
    hour_stats[edt_hour]["likes"] += p["likes"]
    hour_stats[edt_hour]["comments"] += p["comments"]
    hour_stats[edt_hour]["count"] += 1
    
    day_stats[edt_day]["views"] += p["views"]
    day_stats[edt_day]["likes"] += p["likes"]
    day_stats[edt_day]["comments"] += p["comments"]
    day_stats[edt_day]["count"] += 1

# Average per hour of day
hourly_averages = []
for hr in sorted(hour_stats.keys()):
    c = hour_stats[hr]["count"]
    hourly_averages.append({
        "hour_edt": hr,
        "avg_views": round(hour_stats[hr]["views"] / c, 2),
        "avg_likes": round(hour_stats[hr]["likes"] / c, 2),
        "avg_comments": round(hour_stats[hr]["comments"] / c, 2),
        "post_count": c
    })

# Average per day of week
daily_averages = []
for d in sorted(day_stats.keys()):
    c = day_stats[d]["count"]
    daily_averages.append({
        "day": get_day_name(d),
        "avg_views": round(day_stats[d]["views"] / c, 2),
        "avg_likes": round(day_stats[d]["likes"] / c, 2),
        "avg_comments": round(day_stats[d]["comments"] / c, 2),
        "post_count": c
    })

# 2. Impact of Likes vs Comments on Views
no_eng = [p for p in posts if p["likes"] == 0 and p["comments"] == 0]
only_likes = [p for p in posts if p["likes"] > 0 and p["comments"] == 0]
only_comments = [p for p in posts if p["likes"] == 0 and p["comments"] > 0]
both = [p for p in posts if p["likes"] > 0 and p["comments"] > 0]

bracket_stats = {
    "No Engagement": {
        "count": len(no_eng),
        "avg_views": round(sum(p["views"] for p in no_eng) / len(no_eng), 2) if no_eng else 0
    },
    "Only Likes (No Comments)": {
        "count": len(only_likes),
        "avg_views": round(sum(p["views"] for p in only_likes) / len(only_likes), 2) if only_likes else 0
    },
    "Only Comments (No Likes)": {
        "count": len(only_comments),
        "avg_views": round(sum(p["views"] for p in only_comments) / len(only_comments), 2) if only_comments else 0
    },
    "Both (Likes & Comments)": {
        "count": len(both),
        "avg_views": round(sum(p["views"] for p in both) / len(both), 2) if both else 0
    }
}

# 3. Post length vs views & engagement
length_stats = []
for p in posts:
    words = len((p["title"] + " " + p["content"]).split())
    length_stats.append((words, p["views"], p["likes"] + p["comments"]))

short_posts = [x for x in length_stats if x[0] < 30]
med_posts = [x for x in length_stats if 30 <= x[0] < 80]
long_posts = [x for x in length_stats if x[0] >= 80]

length_comparison = {
    "Short (<30 words)": {
        "count": len(short_posts),
        "avg_views": round(sum(x[1] for x in short_posts) / len(short_posts), 2) if short_posts else 0,
        "avg_engagement": round(sum(x[2] for x in short_posts) / len(short_posts), 2) if short_posts else 0
    },
    "Medium (30-80 words)": {
        "count": len(med_posts),
        "avg_views": round(sum(x[1] for x in med_posts) / len(med_posts), 2) if med_posts else 0,
        "avg_engagement": round(sum(x[2] for x in med_posts) / len(med_posts), 2) if med_posts else 0
    },
    "Long (>=80 words)": {
        "count": len(long_posts),
        "avg_views": round(sum(x[1] for x in long_posts) / len(long_posts), 2) if long_posts else 0,
        "avg_engagement": round(sum(x[2] for x in long_posts) / len(long_posts), 2) if long_posts else 0
    }
}

# 4. Topic Categorization
topic_stats = defaultdict(list)
for p in posts:
    text = (p["title"] + " " + p["content"]).lower()
    if any(k in text for k in ["ecom", "spy", "pipiads", "ppspy", "adspy", "ads", "winning product"]):
        topic_stats["E-commerce / Ads"].append(p)
    elif any(k in text for k in ["heygen", "video", "captions", "faceless", "leonardo", "design", "canva", "figma"]):
        topic_stats["Video & Design Tools"].append(p)
    elif any(k in text for k in ["chatgpt", "grok", "perplexity", "ai search", "ai plus"]):
        topic_stats["AI Chat & Assistants"].append(p)
    else:
        topic_stats["Other / General"].append(p)

topic_comparison = {}
for topic, p_list in topic_stats.items():
    topic_comparison[topic] = {
        "count": len(p_list),
        "avg_views": round(sum(p["views"] for p in p_list) / len(p_list), 2),
        "avg_likes": round(sum(p["likes"] for p in p_list) / len(p_list), 2),
        "avg_comments": round(sum(p["comments"] for p in p_list) / len(p_list), 2)
    }

# Save report
deep_report = {
    "hourly_averages": hourly_averages,
    "daily_averages": daily_averages,
    "bracket_stats": bracket_stats,
    "length_comparison": length_comparison,
    "topic_comparison": topic_comparison
}

with open(r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\deep_analysis_report.json", "w", encoding="utf-8") as f:
    json.dump(deep_report, f, indent=2)

print("\n--- DEEP ANALYSIS COMPLETED ---")
print("Bracket Stats compiled successfully.")
