import psutil

pids = [20724, 23044]
for pid in pids:
    print(f"\n=================== PID {pid} ===================")
    try:
        p = psutil.Process(pid)
        env = p.environ()
        # Print a few interesting environment variables
        keys = ["PORT", "WHOP_COMPANY_ID", "BOT_USER_ID", "WHOP_EXPERIENCE_ID", "DISABLE_DASHBOARD"]
        for k in keys:
            print(f"  {k}: {env.get(k)}")
        # Print cmdline
        print(f"  Cmdline: {p.cmdline()}")
    except Exception as e:
        print(f"  Error inspecting PID {pid}: {e}")
