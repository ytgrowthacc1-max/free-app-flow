import os
import sys
import json
import datetime

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
metrics_file = os.path.join(base_dir, ".tmp", "24h_posts_metrics.json")
if not os.path.exists(metrics_file):
    metrics_file = os.path.join(base_dir, ".tmp", "24h_master_posts_metrics.json")

posts = json.load(open(metrics_file, "r", encoding="utf-8"))

# Build route lookup
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

# Sort posts by views descending, then likes, comments
sorted_posts = sorted(posts, key=lambda x: (x.get("view_count", 0), x.get("engagement_score", 0), x.get("like_count", 0)), reverse=True)

# Deduplicate to show the top 50 unique highest-performing posts
top_50 = sorted_posts[:50]

report_lines = []
report_lines.append("# 🏆 Top 50 Most Popular Whop Posts (Last 24 Hours)")
report_lines.append(f"\n> **Generated:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
report_lines.append(f"> **Total Analyzed Posts:** {len(posts):,} posts across 1,914 community channels.")
report_lines.append("\nClick any of the links below to inspect the live post and community on Whop.\n")
report_lines.append("---")

report_lines.append("\n## 📊 Quick Summary Table (Top 25)\n")
report_lines.append("| # | Views | Likes | Comments | Community | Post Title | Links |")
report_lines.append("|---|:---:|:---:|:---:|---|---|---|")

for idx, p in enumerate(top_50[:25], 1):
    pid = p.get("id")
    exp_id = p.get("experience_id", "")
    cid = p.get("company_id", "")
    route_info = routes_map.get(exp_id) or routes_map.get(cid) or {}
    route = route_info.get("route", "")
    
    comp_url = f"https://whop.com/joined/{route}/" if route else f"https://whop.com/experiences/{exp_id}"
    post_url = f"https://whop.com/joined/{route}/?post_id={pid}" if route else f"https://whop.com/experiences/{exp_id}?post={pid}"
    
    title_clean = p.get("title", "Untitled").replace("|", "-")
    comp_name = p.get("company_name", "Whop Community").replace("|", "-")
    views = p.get("view_count", 0)
    likes = p.get("like_count", 0)
    comments = p.get("comment_count", 0)
    
    report_lines.append(f"| **{idx:02d}** | **{views:,}** | {likes} | {comments} | [{comp_name}]({comp_url}) | {title_clean} | [🔗 View Post]({post_url}) |")

report_lines.append("\n---\n")
report_lines.append("## 🔍 Detailed Breakdown of Top Performing Posts\n")

for idx, p in enumerate(top_50, 1):
    pid = p.get("id")
    exp_id = p.get("experience_id", "")
    cid = p.get("company_id", "")
    route_info = routes_map.get(exp_id) or routes_map.get(cid) or {}
    route = route_info.get("route", "")
    
    comp_url = f"https://whop.com/joined/{route}/" if route else f"https://whop.com/experiences/{exp_id}"
    post_url = f"https://whop.com/joined/{route}/?post_id={pid}" if route else f"https://whop.com/experiences/{exp_id}?post={pid}"
    
    title = p.get("title", "Untitled")
    comp_name = p.get("company_name", "Whop Community")
    bot_user = p.get("bot_username", p.get("bot_id", "bot"))
    views = p.get("view_count", 0)
    likes = p.get("like_count", 0)
    comments = p.get("comment_count", 0)
    score = p.get("engagement_score", views + (likes*2) + (comments*3))
    created = p.get("created_at", "N/A")
    content = p.get("content", "").strip()

    report_lines.append(f"### #{idx:02d} — {title}")
    report_lines.append(f"- **Direct Post Link:** [{post_url}]({post_url})")
    report_lines.append(f"- **Community Link:** [{comp_name}]({comp_url}) (`{exp_id}`)")
    report_lines.append(f"- **Metrics:** 👁️ **{views:,} views** &nbsp;|&nbsp; ❤️ **{likes} likes** &nbsp;|&nbsp; 💬 **{comments} comments** &nbsp;|&nbsp; 📈 **Score:** {score}")
    report_lines.append(f"- **Author Bot:** `@{bot_user}` ({p.get('bot_id')})")
    report_lines.append(f"- **Published At:** `{created}`")
    if content:
        report_lines.append(f"- **Content / Hook:**\n> {content.replace(chr(10), ' ')}")
    report_lines.append("\n---")

output_report_path = os.path.join(base_dir, "top_popular_posts_24h.md")
with open(output_report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"[SUCCESS] Report generated successfully at: {output_report_path}")
