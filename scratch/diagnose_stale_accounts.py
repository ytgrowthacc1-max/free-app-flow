import os
import json
import time
import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")
now = datetime.datetime.now()
now_ts = time.time()
weekday = now.strftime("%a").lower()

print(f"--- DIAGNOSING STALE ACCOUNTS (Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}, Day: {weekday.upper()}) ---\n")

results = []

if os.path.exists(bots_dir):
    for bot_id in os.listdir(bots_dir):
        bot_path = os.path.join(bots_dir, bot_id)
        if not os.path.isdir(bot_path):
            continue
        pfile = os.path.join(bot_path, "profile.json")
        bot_name = bot_id
        if os.path.exists(pfile):
            try:
                with open(pfile, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                    bot_name = pdata.get("bot_username", bot_id)
            except Exception:
                pass

        for comp_id in os.listdir(bot_path):
            comp_path = os.path.join(bot_path, comp_id)
            if not os.path.isdir(comp_path):
                continue
            sfile = os.path.join(comp_path, "scheduler_settings.json")
            cfile = os.path.join(comp_path, "company.json")
            if not os.path.exists(sfile):
                continue

            comp_name = comp_id
            if os.path.exists(cfile):
                try:
                    with open(cfile, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                        comp_name = cdata.get("company_name", comp_id)
                except Exception:
                    pass

            try:
                with open(sfile, "r", encoding="utf-8") as f:
                    s = json.load(f)
            except Exception as e:
                continue

            last_run = s.get("last_run_time", 0.0)
            idle_min = (now_ts - last_run) / 60 if last_run > 0 else 99999
            
            master_on = s.get("master_switch_enabled", True)
            sched_on = s.get("scheduler_enabled", False)
            auto_on = s.get("autopilot_enabled", False)
            posts_today = s.get("posts_published_today", 0)
            max_posts = s.get("max_posts_per_day", 3)
            freq_min = s.get("frequency_minutes", 60)
            active_slots = s.get("active_slots", {})
            day_cfg = active_slots.get(weekday, {"enabled": False, "start": "09:00", "end": "17:00"})

            reasons = []
            if not master_on:
                reasons.append("Master kill switch OFF")
            if not sched_on and not auto_on:
                reasons.append("Both Scheduler and Autopilot are OFF")
            if not day_cfg.get("enabled", False):
                reasons.append(f"Day {weekday.upper()} disabled in active_slots")
            else:
                start_str = day_cfg.get("start", "09:00")
                end_str = day_cfg.get("end", "17:00")
                try:
                    sh, sm = map(int, start_str.split(":"))
                    eh, em = map(int, end_str.split(":"))
                    st = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
                    et = now.replace(hour=eh, minute=em, second=0, microsecond=0)
                    if not (st <= now <= et):
                        reasons.append(f"Outside time window ({start_str}-{end_str}, current={now.strftime('%H:%M')})")
                except Exception as ex:
                    reasons.append(f"Time parse error: {ex}")

            if posts_today >= max_posts:
                reasons.append(f"Daily limit reached ({posts_today}/{max_posts})")

            results.append({
                "bot": bot_name,
                "bot_id": bot_id,
                "company": comp_name,
                "comp_id": comp_id,
                "idle_min": idle_min,
                "last_run": datetime.datetime.fromtimestamp(last_run).strftime('%Y-%m-%d %H:%M:%S') if last_run > 0 else "Never",
                "freq_min": freq_min,
                "posts_today": posts_today,
                "max_posts": max_posts,
                "reasons": reasons
            })

# Filter for accounts that are enabled (master_on and (sched_on or auto_on)) and idle > 30 mins
results.sort(key=lambda x: x["idle_min"], reverse=True)

report_lines = []
stale_enabled = [r for r in results if r["idle_min"] > 30 and not any("OFF" in reason for reason in r["reasons"])]
print(f"Found {len(stale_enabled)} ENABLED accounts idle > 30 minutes:\n")

for r in stale_enabled[:30]:
    line = f"[{r['bot']}] Community: {r['company']}\n  Idle: {r['idle_min']:.1f} mins | Last Run: {r['last_run']} | Freq: {r['freq_min']}m | Posts Today: {r['posts_today']}/{r['max_posts']}\n  Reasons skipping: {', '.join(r['reasons']) if r['reasons'] else 'NONE (SHOULD BE RUNNING!)'}\n"
    print(line)
    report_lines.append(line)

with open(os.path.join(os.path.dirname(__file__), "stale_diag.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
