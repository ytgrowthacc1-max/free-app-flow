import os
import sys
import json
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
metrics_file = os.path.join(base_dir, ".tmp", "24h_posts_metrics.json")
if not os.path.exists(metrics_file):
    metrics_file = os.path.join(base_dir, ".tmp", "24h_master_posts_metrics.json")

raw_posts = json.load(open(metrics_file, "r", encoding="utf-8"))

# Build bot token map and route lookup
bots_dir = os.path.join(base_dir, "profiles", "bots")
routes_map = {}
bot_tokens = {}

for b in os.listdir(bots_dir):
    bdir = os.path.join(bots_dir, b)
    if not os.path.isdir(bdir): continue
    pfile = os.path.join(bdir, "profile.json")
    if os.path.exists(pfile):
        try:
            pdata = json.load(open(pfile, "r", encoding="utf-8"))
            if pdata.get("oauth_token"):
                bot_tokens[b] = pdata["oauth_token"]
        except Exception:
            pass
            
    for c in os.listdir(bdir):
        cdir = os.path.join(bdir, c)
        cfile = os.path.join(cdir, "company.json")
        if os.path.exists(cfile):
            try:
                cdata = json.load(open(cfile, "r", encoding="utf-8"))
                cid = cdata.get("company_id", c)
                exp_id = cdata.get("experience_id", "")
                route = cdata.get("route", "")
                routes_map[cid] = {"route": route, "exp_id": exp_id, "name": cdata.get("company_name", "")}
                if exp_id:
                    routes_map[exp_id] = {"route": route, "cid": cid, "name": cdata.get("company_name", "")}
            except Exception:
                pass

# Sort raw posts to find top 50
sorted_posts = sorted(raw_posts, key=lambda x: (x.get("view_count", 0), x.get("engagement_score", 0), x.get("like_count", 0)), reverse=True)
top_50_basic = sorted_posts[:50]

print(f"Fetching full post details (poll options, full content, comments) for top 50 posts...", flush=True)

def fetch_full_post_details(p):
    pid = p.get("id")
    bot_id = p.get("bot_id")
    token = bot_tokens.get(bot_id)
    if not token and bot_tokens:
        token = next(iter(bot_tokens.values()))
        
    full_data = dict(p)
    if token and pid:
        try:
            url = f"https://api.whop.com/api/v1/forum_posts/{pid}"
            r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=8)
            if r.status_code == 200:
                d = r.json()
                full_data["full_content"] = d.get("content", "")
                full_data["title"] = d.get("title") or full_data.get("title")
                full_data["view_count"] = d.get("view_count", full_data.get("view_count", 0))
                full_data["like_count"] = d.get("like_count", full_data.get("like_count", 0))
                full_data["comment_count"] = d.get("comment_count", full_data.get("comment_count", 0))
                full_data["attachments"] = d.get("attachments", [])
        except Exception:
            pass
    return full_data

enriched_posts = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_full_post_details, p) for p in top_50_basic]
    for f in as_completed(futures):
        enriched_posts.append(f.result())

# Re-sort enriched
enriched_posts = sorted(enriched_posts, key=lambda x: (x.get("view_count", 0), x.get("engagement_score", 0), x.get("like_count", 0)), reverse=True)

# Build Markdown File
md_lines = []
md_lines.append("# 🏆 Top 50 Most Popular Whop Posts (Last 24 Hours)")
md_lines.append(f"\n> **Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
md_lines.append("> **Direct Post URLs:** Clicking any `[🔗 Direct Post]` link opens that specific post on Whop (`https://whop.com/posts/{post_id}/`).")
md_lines.append("\n---\n")

md_lines.append("## 📊 Quick Summary Table (Top 25 Posts)\n")
md_lines.append("| # | Views | Likes | Comments | Community | Post Title | Direct Post Link | Hub Post Link |")
md_lines.append("|---|:---:|:---:|:---:|---|---|---|---|")

for idx, p in enumerate(enriched_posts[:25], 1):
    pid = p.get("id")
    exp_id = p.get("experience_id", "")
    cid = p.get("company_id", "")
    route_info = routes_map.get(exp_id) or routes_map.get(cid) or {}
    route = route_info.get("route", "")
    
    direct_post_url = f"https://whop.com/posts/{pid}/"
    hub_post_url = f"https://whop.com/hub/{exp_id}/{pid}/" if exp_id else direct_post_url
    comp_url = f"https://whop.com/joined/{route}/" if route else f"https://whop.com/experiences/{exp_id}"
    
    title_clean = p.get("title", "Untitled").replace("|", "-")
    comp_name = p.get("company_name", "Whop Community").replace("|", "-")
    views = p.get("view_count", 0)
    likes = p.get("like_count", 0)
    comments = p.get("comment_count", 0)
    
    md_lines.append(f"| **{idx:02d}** | **{views:,}** | {likes} | {comments} | [{comp_name}]({comp_url}) | {title_clean} | [🔗 Direct Post]({direct_post_url}) | [🌐 Hub Post]({hub_post_url}) |")

md_lines.append("\n---\n")
md_lines.append("## 🔍 Detailed Post Breakdown & Full Content (Top 50)\n")

for idx, p in enumerate(enriched_posts, 1):
    pid = p.get("id")
    exp_id = p.get("experience_id", "")
    cid = p.get("company_id", "")
    route_info = routes_map.get(exp_id) or routes_map.get(cid) or {}
    route = route_info.get("route", "")
    
    direct_post_url = f"https://whop.com/posts/{pid}/"
    hub_post_url = f"https://whop.com/hub/{exp_id}/{pid}/" if exp_id else direct_post_url
    comp_url = f"https://whop.com/joined/{route}/" if route else f"https://whop.com/experiences/{exp_id}"
    
    title = p.get("title", "Untitled")
    comp_name = p.get("company_name", "Whop Community")
    bot_user = p.get("bot_username", p.get("bot_id", "bot"))
    views = p.get("view_count", 0)
    likes = p.get("like_count", 0)
    comments = p.get("comment_count", 0)
    score = p.get("engagement_score", views + (likes*2) + (comments*3))
    created = p.get("created_at", "N/A")
    content = (p.get("full_content") or p.get("content") or "").strip()

    md_lines.append(f"### #{idx:02d} — {title}")
    md_lines.append(f"- **Direct Post URL:** [{direct_post_url}]({direct_post_url})")
    md_lines.append(f"- **Hub Post URL:** [{hub_post_url}]({hub_post_url})")
    md_lines.append(f"- **Community:** [{comp_name}]({comp_url}) (`{exp_id}`)")
    md_lines.append(f"- **Stats:** 👁️ **{views:,} views** &nbsp;|&nbsp; ❤️ **{likes} likes** &nbsp;|&nbsp; 💬 **{comments} comments** &nbsp;|&nbsp; 📈 **Engagement Score:** {score}")
    md_lines.append(f"- **Author Bot:** `@{bot_user}` ({p.get('bot_id')})")
    md_lines.append(f"- **Published Timestamp:** `{created}`")
    if content:
        md_lines.append(f"- **Full Post Body & Offer:**\n\n```text\n{content}\n```")
    md_lines.append("\n---")

output_md_path = os.path.join(base_dir, "top_popular_posts_24h.md")
with open(output_md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

# Build Clean Standalone HTML Viewer
html_cards = []
for idx, p in enumerate(enriched_posts, 1):
    pid = p.get("id")
    exp_id = p.get("experience_id", "")
    cid = p.get("company_id", "")
    route_info = routes_map.get(exp_id) or routes_map.get(cid) or {}
    route = route_info.get("route", "")
    
    direct_post_url = f"https://whop.com/posts/{pid}/"
    hub_post_url = f"https://whop.com/hub/{exp_id}/{pid}/" if exp_id else direct_post_url
    comp_url = f"https://whop.com/joined/{route}/" if route else f"https://whop.com/experiences/{exp_id}"
    
    title = p.get("title", "Untitled")
    comp_name = p.get("company_name", "Whop Community")
    bot_user = p.get("bot_username", p.get("bot_id", "bot"))
    views = p.get("view_count", 0)
    likes = p.get("like_count", 0)
    comments = p.get("comment_count", 0)
    created = p.get("created_at", "N/A")
    content = (p.get("full_content") or p.get("content") or "").strip()
    
    html_cards.append(f"""
    <div class="post-card">
        <div class="card-header">
            <span class="rank-badge">#{idx:02d}</span>
            <div class="meta-right">
                <span class="stat-pill views">👁️ {views:,} views</span>
                <span class="stat-pill likes">❤️ {likes} likes</span>
                <span class="stat-pill comments">💬 {comments} comments</span>
            </div>
        </div>
        <h3 class="post-title">{title}</h3>
        <div class="community-info">
            <span>🏢 <a href="{comp_url}" target="_blank">{comp_name}</a></span>
            <span>👤 @{bot_user}</span>
            <span>🕒 {created[:19].replace('T', ' ')}</span>
        </div>
        <div class="post-content">
            <pre>{content}</pre>
        </div>
        <div class="card-actions">
            <a href="{direct_post_url}" target="_blank" class="btn btn-primary">🔗 Open Direct Post</a>
            <a href="{hub_post_url}" target="_blank" class="btn btn-secondary">🌐 Open in Hub</a>
            <a href="{comp_url}" target="_blank" class="btn btn-outline">Community Page</a>
        </div>
    </div>
    """)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top 50 Most Popular Whop Posts (Last 24 Hours)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #090a0f;
            --bg-card: rgba(20, 24, 36, 0.85);
            --border-card: rgba(255, 255, 255, 0.08);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --accent-glow: #6366f1;
            --accent-grad: linear-gradient(135deg, #6366f1, #a855f7);
            --pill-views: rgba(99, 102, 241, 0.2);
            --pill-likes: rgba(244, 63, 94, 0.2);
            --pill-comments: rgba(16, 185, 129, 0.2);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            padding: 30px 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 25px;
            border-bottom: 1px solid var(--border-card);
        }}
        header h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        header p {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}
        .search-bar {{
            width: 100%;
            padding: 14px 18px;
            background: #111420;
            border: 1px solid #282e44;
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
            margin-bottom: 30px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-bar:focus {{
            border-color: #6366f1;
        }}
        .posts-grid {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .post-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 14px;
            padding: 24px;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .post-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.4);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }}
        .rank-badge {{
            font-size: 1rem;
            font-weight: 800;
            color: #6366f1;
            background: rgba(99, 102, 241, 0.15);
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }}
        .meta-right {{
            display: flex;
            gap: 8px;
        }}
        .stat-pill {{
            font-size: 0.85rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
        }}
        .stat-pill.views {{ background: var(--pill-views); color: #818cf8; }}
        .stat-pill.likes {{ background: var(--pill-likes); color: #fb7185; }}
        .stat-pill.comments {{ background: var(--pill-comments); color: #34d399; }}
        .post-title {{
            font-size: 1.3rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 12px;
            color: #ffffff;
        }}
        .community-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}
        .community-info a {{
            color: #a5b4fc;
            text-decoration: none;
            font-weight: 600;
        }}
        .community-info a:hover {{ text-decoration: underline; }}
        .post-content {{
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 18px;
            border: 1px solid rgba(255,255,255,0.04);
        }}
        .post-content pre {{
            white-space: pre-wrap;
            word-break: break-word;
            font-family: inherit;
            font-size: 0.92rem;
            color: #cbd5e1;
            line-height: 1.5;
        }}
        .card-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .btn {{
            text-decoration: none;
            font-size: 0.88rem;
            font-weight: 600;
            padding: 9px 18px;
            border-radius: 8px;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .btn-primary {{
            background: var(--accent-grad);
            color: #ffffff;
            box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
        }}
        .btn-primary:hover {{
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.5);
            transform: translateY(-1px);
        }}
        .btn-secondary {{
            background: #1e2438;
            color: #e2e8f0;
            border: 1px solid #334155;
        }}
        .btn-secondary:hover {{
            background: #28304a;
        }}
        .btn-outline {{
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .btn-outline:hover {{
            color: #fff;
            border-color: rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏆 Top 50 Most Popular Whop Posts (Last 24 Hours)</h1>
            <p>Direct access to each post, verified live stats, and complete offer text across the entire automation fleet.</p>
        </header>

        <input type="text" class="search-bar" id="search" placeholder="Search by title, community, bot username, or keyword..." oninput="filterPosts()">

        <div class="posts-grid" id="postsGrid">
            {"".join(html_cards)}
        </div>
    </div>

    <script>
        function filterPosts() {{
            const query = document.getElementById('search').value.toLowerCase();
            const cards = document.querySelectorAll('.post-card');
            cards.forEach(card => {{
                const text = card.innerText.toLowerCase();
                if (text.includes(query)) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

output_html_path = os.path.join(base_dir, "top_popular_posts_24h.html")
with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SUCCESS] Markdown report generated: {output_md_path}")
print(f"[SUCCESS] Interactive HTML page generated: {output_html_path}")
