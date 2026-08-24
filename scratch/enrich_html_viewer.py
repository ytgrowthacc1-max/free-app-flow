import os
import sys
import json
import datetime
import re

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
metrics_file = os.path.join(base_dir, ".tmp", "24h_posts_metrics.json")
if not os.path.exists(metrics_file):
    metrics_file = os.path.join(base_dir, ".tmp", "24h_master_posts_metrics.json")

posts = json.load(open(metrics_file, "r", encoding="utf-8"))

# Load route map
bots_dir = os.path.join(base_dir, "profiles", "bots")
routes_map = {}
for b in os.listdir(bots_dir):
    bdir = os.path.join(bots_dir, b)
    if not os.path.isdir(bdir): continue
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

# Sort posts
sorted_posts = sorted(posts, key=lambda x: (x.get("view_count", 0), x.get("engagement_score", 0), x.get("like_count", 0)), reverse=True)
top_50 = sorted_posts[:50]

def categorize_post(title):
    t = title.lower()
    if any(k in t for k in ["clearance", "deal", "discount", "price mistake", "penny", "arbitrage", "retail", "walmart", "target", "lowe's", "resell"]):
        return "Deals & Arbitrage", "badge-deals"
    if any(k in t for k in ["pokemon", "tcg", "card", "charizard", "booster", "grading", "restock", "151"]):
        return "Pokemon & TCG", "badge-pokemon"
    if any(k in t for k in ["pick", "parlay", "bet", "odds", "slip", "sportsbook", "ufc", "nba", "closing line"]):
        return "Sports Betting", "badge-betting"
    if any(k in t for k in ["crypto", "token", "solana", "memecoin", "trading", "market", "trade"]):
        return "Crypto & Trading", "badge-trading"
    if any(k in t for k in ["clip", "tiktok", "reels", "shorts", "editor", "video", "capcut", "bounty"]):
        return "Video Clipping", "badge-clipping"
    if any(k in t for k in ["saas", "nocode", "app", "software", "tool", "builder", "mrr"]):
        return "NoCode & SaaS", "badge-saas"
    return "General Growth", "badge-general"

cards_html = []

for idx, p in enumerate(top_50, 1):
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
    cat_name, cat_class = categorize_post(title)
    
    # Extract affiliate link if present in content
    aff_links = re.findall(r'https?://(?:[a-zA-Z0-9-]+\.)*whop\.com[^\s\)\]\"\'\>]*', content)
    aff_link = aff_links[0] if aff_links else ""

    cards_html.append(f"""
    <div class="post-card" data-category="{cat_name}" data-views="{views}" data-likes="{likes}" data-comments="{comments}" data-index="{idx}">
        <div class="card-header">
            <div class="header-left">
                <span class="rank-badge">#{idx:02d}</span>
                <span class="category-tag {cat_class}">{cat_name}</span>
            </div>
            <div class="meta-right">
                <span class="stat-pill views" title="Verified Whop Views">👁️ {views:,} views</span>
                <span class="stat-pill likes" title="Likes">❤️ {likes}</span>
                <span class="stat-pill comments" title="Comments & CTAs">💬 {comments}</span>
            </div>
        </div>

        <h3 class="post-title">{title}</h3>

        <div class="community-info">
            <span class="info-item">🏢 Community: <a href="{comp_url}" target="_blank" rel="noopener">{comp_name}</a></span>
            <span class="info-item">👤 Author: <strong>@{bot_user}</strong></span>
            <span class="info-item">🕒 {created[:19].replace('T', ' ')} UTC</span>
        </div>

        <div class="post-content">
            <pre>{content}</pre>
        </div>

        {f'<div class="affiliate-preview">🎯 <strong>Embedded Target:</strong> <a href="{aff_link}" target="_blank" rel="noopener">{aff_link}</a></div>' if aff_link else ''}

        <div class="card-actions">
            <a href="{direct_post_url}" target="_blank" rel="noopener" class="btn btn-primary">
                <span>🔗</span> Open Direct Post
            </a>
            <a href="{hub_post_url}" target="_blank" rel="noopener" class="btn btn-secondary">
                <span>🌐</span> Hub App View
            </a>
            <button class="btn btn-outline" onclick="copyUrl('{direct_post_url}', this)">
                <span>📋</span> Copy Post Link
            </button>
        </div>
    </div>
    """)

html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top 50 Most Popular Whop Posts (Last 24 Hours) — Live Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #08090d;
            --bg-card: rgba(17, 21, 34, 0.75);
            --bg-card-hover: rgba(22, 28, 46, 0.95);
            --border-card: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(99, 102, 241, 0.4);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-grad: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --pill-views: rgba(99, 102, 241, 0.18);
            --pill-likes: rgba(244, 63, 94, 0.18);
            --pill-comments: rgba(16, 185, 129, 0.18);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-body);
            color: var(--text-main);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            padding: 40px 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1080px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 35px;
            padding-bottom: 25px;
            border-bottom: 1px solid var(--border-card);
        }}
        .badge-live {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 12px;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .live-dot {{
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(1.2); }}
        }}
        header h1 {{
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #ffffff 40%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        header p {{
            color: var(--text-muted);
            font-size: 1.05rem;
            max-width: 650px;
            margin: 0 auto;
        }}
        
        /* Filter Controls */
        .controls-panel {{
            background: #0f1320;
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }}
        .search-row {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }}
        .search-bar {{
            flex: 1;
            padding: 13px 18px;
            background: #171c2e;
            border: 1px solid #2d3550;
            border-radius: 10px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-bar:focus {{
            border-color: #6366f1;
        }}
        .sort-select {{
            padding: 13px 16px;
            background: #171c2e;
            border: 1px solid #2d3550;
            border-radius: 10px;
            color: #f1f5f9;
            font-size: 0.92rem;
            outline: none;
            cursor: pointer;
        }}
        .category-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .filter-chip {{
            background: #171c2e;
            color: var(--text-muted);
            border: 1px solid #2a3148;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .filter-chip:hover {{
            background: #232a42;
            color: #fff;
        }}
        .filter-chip.active {{
            background: #6366f1;
            color: #fff;
            border-color: #6366f1;
            box-shadow: 0 2px 10px rgba(99, 102, 241, 0.4);
        }}

        /* Post Cards */
        .posts-grid {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .post-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(16px);
            box-shadow: 0 6px 24px rgba(0,0,0,0.3);
            transition: all 0.25s ease;
        }}
        .post-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-highlight);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .rank-badge {{
            font-size: 1rem;
            font-weight: 800;
            color: #a5b4fc;
            background: rgba(99, 102, 241, 0.2);
            padding: 4px 12px;
            border-radius: 8px;
            border: 1px solid rgba(99, 102, 241, 0.35);
        }}
        .category-tag {{
            font-size: 0.78rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge-deals {{ background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }}
        .badge-pokemon {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
        .badge-betting {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-trading {{ background: rgba(14, 165, 233, 0.2); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.4); }}
        .badge-clipping {{ background: rgba(217, 70, 239, 0.2); color: #e879f9; border: 1px solid rgba(217, 70, 239, 0.4); }}
        .badge-saas {{ background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.4); }}
        .badge-general {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }}

        .meta-right {{
            display: flex;
            gap: 8px;
        }}
        .stat-pill {{
            font-size: 0.88rem;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
        }}
        .stat-pill.views {{ background: var(--pill-views); color: #a5b4fc; }}
        .stat-pill.likes {{ background: var(--pill-likes); color: #fb7185; }}
        .stat-pill.comments {{ background: var(--pill-comments); color: #4ade80; }}

        .post-title {{
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.35;
            color: #ffffff;
            margin-bottom: 12px;
        }}
        .community-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-bottom: 16px;
        }}
        .community-info a {{
            color: #c7d2fe;
            text-decoration: none;
            font-weight: 600;
        }}
        .community-info a:hover {{ text-decoration: underline; }}
        
        .post-content {{
            background: rgba(8, 10, 18, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 14px;
        }}
        .post-content pre {{
            white-space: pre-wrap;
            word-break: break-word;
            font-family: inherit;
            font-size: 0.94rem;
            color: #cbd5e1;
            line-height: 1.55;
        }}

        .affiliate-preview {{
            font-size: 0.85rem;
            color: #94a3b8;
            margin-bottom: 16px;
            background: rgba(99, 102, 241, 0.08);
            border: 1px dashed rgba(99, 102, 241, 0.3);
            padding: 8px 12px;
            border-radius: 8px;
            word-break: break-all;
        }}
        .affiliate-preview a {{
            color: #818cf8;
            font-family: 'JetBrains Mono', monospace;
            text-decoration: none;
        }}
        .affiliate-preview a:hover {{ text-decoration: underline; }}

        .card-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .btn {{
            font-size: 0.88rem;
            font-weight: 600;
            padding: 9px 18px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 7px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
        }}
        .btn-primary {{
            background: var(--accent-grad);
            color: #ffffff;
            box-shadow: 0 3px 12px rgba(99, 102, 241, 0.35);
        }}
        .btn-primary:hover {{
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.55);
            transform: translateY(-1px);
        }}
        .btn-secondary {{
            background: #1f263d;
            color: #e2e8f0;
            border: 1px solid #333e61;
        }}
        .btn-secondary:hover {{
            background: #2a3454;
        }}
        .btn-outline {{
            background: transparent;
            color: var(--text-muted);
            border: 1px solid rgba(255,255,255,0.12);
        }}
        .btn-outline:hover {{
            color: #fff;
            border-color: rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.04);
        }}
        
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: #fff;
            padding: 12px 22px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 9999;
        }}
        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge-live">
                <span class="live-dot"></span>
                <span>LIVE FLEET METRICS & DIRECT POST VIEWER</span>
            </div>
            <h1>🏆 Top 50 Most Popular Whop Posts</h1>
            <p>Every post includes direct URL scheme links (<code>https://whop.com/posts/{{id}}/</code>) that bypass group homepages to open the post directly.</p>
        </header>

        <div class="controls-panel">
            <div class="search-row">
                <input type="text" class="search-bar" id="search" placeholder="Search by post title, community, author @handle, or keyword..." oninput="applyFilters()">
                <select class="sort-select" id="sortSelect" onchange="applySorting()">
                    <option value="views">Sort by: Highest Views</option>
                    <option value="likes">Sort by: Most Likes</option>
                    <option value="comments">Sort by: Most Comments</option>
                    <option value="rank">Sort by: Default Rank (#1 - #50)</option>
                </select>
            </div>
            <div class="category-filters">
                <button class="filter-chip active" onclick="setCategory('All', this)">All Niches (50)</button>
                <button class="filter-chip" onclick="setCategory('Deals & Arbitrage', this)">⚡ Deals & Arbitrage</button>
                <button class="filter-chip" onclick="setCategory('Pokemon & TCG', this)">🃏 Pokemon & TCG</button>
                <button class="filter-chip" onclick="setCategory('Sports Betting', this)">🎯 Sports Betting</button>
                <button class="filter-chip" onclick="setCategory('Crypto & Trading', this)">📈 Crypto & Trading</button>
                <button class="filter-chip" onclick="setCategory('Video Clipping', this)">🎬 Video Clipping</button>
                <button class="filter-chip" onclick="setCategory('NoCode & SaaS', this)">💻 NoCode & SaaS</button>
            </div>
        </div>

        <div class="posts-grid" id="postsGrid">
            {"".join(cards_html)}
        </div>
    </div>

    <div class="toast" id="toast">Link copied to clipboard!</div>

    <script>
        let currentCategory = 'All';

        function setCategory(cat, btn) {{
            currentCategory = cat;
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            applyFilters();
        }}

        function applyFilters() {{
            const query = document.getElementById('search').value.toLowerCase();
            const cards = document.querySelectorAll('.post-card');
            cards.forEach(card => {{
                const cat = card.getAttribute('data-category');
                const text = card.innerText.toLowerCase();
                const matchesCat = (currentCategory === 'All' || cat === currentCategory);
                const matchesSearch = (!query || text.includes(query));
                
                if (matchesCat && matchesSearch) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function applySorting() {{
            const sortBy = document.getElementById('sortSelect').value;
            const grid = document.getElementById('postsGrid');
            const cards = Array.from(grid.querySelectorAll('.post-card'));

            cards.sort((a, b) => {{
                if (sortBy === 'views') {{
                    return parseInt(b.getAttribute('data-views')) - parseInt(a.getAttribute('data-views'));
                }} else if (sortBy === 'likes') {{
                    return parseInt(b.getAttribute('data-likes')) - parseInt(a.getAttribute('data-likes'));
                }} else if (sortBy === 'comments') {{
                    return parseInt(b.getAttribute('data-comments')) - parseInt(a.getAttribute('data-comments'));
                }} else {{
                    return parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index'));
                }}
            }});

            cards.forEach(card => grid.appendChild(card));
        }}

        function copyUrl(url, btn) {{
            navigator.clipboard.writeText(url).then(() => {{
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                const origText = btn.innerHTML;
                btn.innerHTML = '<span>✅</span> Copied!';
                setTimeout(() => {{
                    toast.classList.remove('show');
                    btn.innerHTML = origText;
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>
"""

output_html_path = os.path.join(base_dir, "top_popular_posts_24h.html")
with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(html_doc)

print(f"[SUCCESS] Rich interactive HTML updated at: {output_html_path}")
