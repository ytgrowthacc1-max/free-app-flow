import os
import json
import time
import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, 'profiles', 'bots')
now = time.time()

report = []
for bot_id in sorted(os.listdir(bots_dir)):
    bpath = os.path.join(bots_dir, bot_id)
    if not os.path.isdir(bpath):
        continue
    pfile = os.path.join(bpath, 'profile.json')
    if not os.path.exists(pfile):
        continue
    try:
        with open(pfile, 'r', encoding='utf-8') as f:
            pdata = json.load(f)
    except Exception:
        continue

    bot_user = pdata.get('bot_username', bot_id)
    token_inv = pdata.get('refresh_token_invalid', False)
    suspended = pdata.get('suspended', False)
    has_token = bool(pdata.get('oauth_token'))
    has_refresh = bool(pdata.get('refresh_token'))
    
    for cname in sorted(os.listdir(bpath)):
        cpath = os.path.join(bpath, cname)
        if not os.path.isdir(cpath):
            continue
        cfile = os.path.join(cpath, 'company.json')
        sfile = os.path.join(cpath, 'scheduler_settings.json')
        if not os.path.exists(cfile) or not os.path.exists(sfile):
            continue
        try:
            with open(cfile, 'r', encoding='utf-8') as f:
                cdata = json.load(f)
            with open(sfile, 'r', encoding='utf-8') as f:
                sdata = json.load(f)
        except Exception:
            continue
            
        comp_name = cdata.get('company_name', cname)
        comp_id = cdata.get('company_id', cname)
        master_on = sdata.get('master_switch_enabled', True)
        sched_on = sdata.get('scheduler_enabled', False)
        auto_on = sdata.get('autopilot_enabled', False)
        exp_id = sdata.get('experience_id', cdata.get('experience_id', ''))
        last_run = sdata.get('last_run_time', 0)
        posts_today = sdata.get('posts_published_today', 0)
        max_today = sdata.get('max_posts_per_day', 3)
        freq = sdata.get('frequency_minutes', 60)
        rand_delay = sdata.get('random_delay_max_minutes', 0)
        
        mins_since_last = (now - last_run) / 60.0 if last_run else 9999
        
        report.append({
            'bot_id': bot_id,
            'bot_user': bot_user,
            'comp_id': comp_id,
            'comp_name': comp_name,
            'master_on': master_on,
            'sched_on': sched_on,
            'auto_on': auto_on,
            'is_active': master_on and (sched_on or auto_on),
            'has_token': has_token,
            'has_refresh': has_refresh,
            'token_inv': token_inv,
            'suspended': suspended,
            'has_exp': bool(exp_id),
            'exp_id': exp_id,
            'last_run': last_run,
            'mins_since_last': round(mins_since_last, 1),
            'posts_today': posts_today,
            'max_today': max_today,
            'freq': freq,
            'rand_delay': rand_delay
        })

print(f"Total configured companies across all bots: {len(report)}")
active = [r for r in report if r['is_active']]
print(f"Total ACTIVE scheduler/autopilot enabled communities: {len(active)}")

posted_recently = [r for r in active if r['mins_since_last'] < 50]
not_posted_50m = [r for r in active if r['mins_since_last'] >= 50]

print(f"Active communities posted within last 50m: {len(posted_recently)}")
print(f"Active communities NOT posted in > 50m: {len(not_posted_50m)}")

# Group reasons for not posting in > 50m
print("\nDetailed list of active communities not posted in > 50m:")
for r in not_posted_50m:
    reasons = []
    if r['suspended']:
        reasons.append("ACCOUNT_SUSPENDED")
    if r['token_inv']:
        reasons.append("REFRESH_TOKEN_INVALID")
    if not r['has_token']:
        reasons.append("NO_OAUTH_TOKEN")
    if not r['has_exp']:
        reasons.append("NO_EXPERIENCE_ID")
    if r['posts_today'] >= r['max_today']:
        reasons.append(f"DAILY_LIMIT_REACHED({r['posts_today']}/{r['max_today']})")
    if not reasons:
        reasons.append(f"IN_QUEUE_WAITING_FREQUENCY(freq={r['freq']}m, last_run={r['mins_since_last']}m ago)")
    
    print(f"  @{r['bot_user']} ({r['bot_id']}) -> {r['comp_name']} ({r['comp_id']}): {r['mins_since_last']}m ago (Today: {r['posts_today']}/{r['max_today']}) -> {', '.join(reasons)}")
