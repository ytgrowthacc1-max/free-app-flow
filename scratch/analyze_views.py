import os
import sys
import datetime
import requests
import json
from collections import Counter
import re

# Add execution dir to path to import whop_auth
sys.path.append(r"c:\Python\WHOP AUTOMATION AGENTIC\execution")
try:
    from whop_auth import get_fresh_token
except ImportError:
    from execution.whop_auth import get_fresh_token

token = get_fresh_token("user_7ziL4hNckh6Ei")
if not token:
    print("Error: Could not get token for user_7ziL4hNckh6Ei")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

exp_id = "exp_KgzMrM89tl4khe"
now = datetime.datetime.now(datetime.timezone.utc)
cutoff = now - datetime.timedelta(days=7)

print(f"Fetching posts since {cutoff.isoformat()} for experience {exp_id}...")

def parse_created_at(dt_str):
    if not dt_str:
        return None
    try:
        cleaned = dt_str.replace("Z", "+00:00")
        return datetime.datetime.fromisoformat(cleaned)
    except Exception:
        try:
            t_part = dt_str.split(".")[0].replace("Z", "")
            return datetime.datetime.strptime(t_part, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        except Exception:
            return None

all_posts = []
seen_ids = set()
cursor = None
limit = 50
cutoff_reached = False

for page_idx in range(1, 25): # fetch up to 1200 posts
    url = f"https://api.whop.com/api/v1/forum_posts?experience_id={exp_id}&limit={limit}"
    if cursor:
        url += f"&after={cursor}"
    
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f"Error fetching page {page_idx}: {r.status_code} - {r.text}")
        break
        
    res = r.json()
    data = res.get("data", [])
    if not data:
        break
        
    new_added = 0
    for p in data:
        pid = p.get("id")
        if pid and pid not in seen_ids:
            p_created = parse_created_at(p.get("created_at"))
            if p_created and p_created < cutoff:
                cutoff_reached = True
                continue
            seen_ids.add(pid)
            all_posts.append(p)
            new_added += 1
            
    if cutoff_reached or new_added == 0:
        break
        
    page_info = res.get("page_info", {})
    if not page_info.get("has_next_page"):
        break
    cursor = page_info.get("end_cursor")
    if not cursor:
        break

print(f"Total posts fetched in last 7 days: {len(all_posts)}")
if not all_posts:
    print("No posts found.")
    sys.exit(0)

# Filter top-level posts
top_posts = [p for p in all_posts if not p.get("parent_id")]
print(f"Top level posts: {len(top_posts)}")

# Build analysis
analyzed_posts = []
for p in top_posts:
    pid = p.get("id")
    title = p.get("title") or "Untitled"
    content = p.get("content") or ""
    views = p.get("view_count") or 0
    likes = p.get("like_count") or 0
    comments = p.get("comment_count") or 0
    created_at = p.get("created_at")
    
    analyzed_posts.append({
        "id": pid,
        "title": title,
        "content": content,
        "views": views,
        "likes": likes,
        "comments": comments,
        "created_at": created_at
    })

# Write JSON
output_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\analyzed_posts.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(analyzed_posts, f, indent=2)

# Analyze correlation and factors
# Top posts by views
top_by_views = sorted(analyzed_posts, key=lambda x: x["views"], reverse=True)[:10]

# Correlation between Views and Likes/Comments
avg_views = sum(p["views"] for p in analyzed_posts) / len(analyzed_posts)
avg_likes = sum(p["likes"] for p in analyzed_posts) / len(analyzed_posts)
avg_comments = sum(p["comments"] for p in analyzed_posts) / len(analyzed_posts)

# Simple correlation calculation
def correlation(x, y):
    n = len(x)
    if n == 0: return 0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
    var_x = sum((x[i] - mean_x)**2 for i in range(n)) / n
    var_y = sum((y[i] - mean_y)**2 for i in range(n)) / n
    std_x = var_x**0.5
    std_y = var_y**0.5
    if std_x == 0 or std_y == 0: return 0
    return cov / (std_x * std_y)

views_list = [p["views"] for p in analyzed_posts]
likes_list = [p["likes"] for p in analyzed_posts]
comments_list = [p["comments"] for p in analyzed_posts]

corr_views_likes = correlation(views_list, likes_list)
corr_views_comments = correlation(views_list, comments_list)

# Topic / Keyword analysis on top viewed posts vs others
def extract_words(text):
    words = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())
    # remove common stopwords
    stopwords = {'the', 'and', 'you', 'for', 'this', 'that', 'with', 'your', 'are', 'was', 'but', 'not', 'have', 'from', 'this', 'here', 'will', 'our', 'out', 'all', 'how', 'what', 'can', 'new', 'get', 'use', 'free', 'about', 'just', 'more', 'some', 'has'}
    return [w for w in words if w not in stopwords]

top_50_viewed_text = " ".join([p["title"] + " " + p["content"] for p in sorted(analyzed_posts, key=lambda x: x["views"], reverse=True)[:50]])
bottom_50_viewed_text = " ".join([p["title"] + " " + p["content"] for p in sorted(analyzed_posts, key=lambda x: x["views"])[:50]])

top_words = Counter(extract_words(top_50_viewed_text)).most_common(15)
bottom_words = Counter(extract_words(bottom_50_viewed_text)).most_common(15)

report = {
    "summary": {
        "total_posts": len(analyzed_posts),
        "avg_views": round(avg_views, 2),
        "avg_likes": round(avg_likes, 2),
        "avg_comments": round(avg_comments, 2),
        "corr_views_likes": round(corr_views_likes, 4),
        "corr_views_comments": round(corr_views_comments, 4),
    },
    "top_posts_by_views": [
        {
            "title": p["title"],
            "views": p["views"],
            "likes": p["likes"],
            "comments": p["comments"],
            "snippet": p["content"][:200]
        } for p in top_by_views
    ],
    "top_keywords_high_views": top_words,
    "top_keywords_low_views": bottom_words
}

report_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\view_analysis_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("\n--- ANALYSIS COMPLETED ---")
print(f"Total posts: {len(analyzed_posts)}")
print(f"Avg Views: {avg_views:.2f}, Likes: {avg_likes:.2f}, Comments: {avg_comments:.2f}")
print(f"Correlation (Views vs Likes): {corr_views_likes:.4f}")
print(f"Correlation (Views vs Comments): {corr_views_comments:.4f}")
print("Top keywords in highly-viewed posts:", top_words)
