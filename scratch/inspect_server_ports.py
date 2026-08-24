import psutil

print("Active Python Listeners:")
for conn in psutil.net_connections(kind='inet'):
    if conn.status == 'LISTEN':
        # Find the process
        try:
            p = psutil.Process(conn.pid)
            if 'python' in p.name().lower():
                print(f"PID {conn.pid:5d} | Port {conn.laddr.port:5d} | Cmd: {' '.join(p.cmdline()[:3])}")
        except Exception:
            pass
