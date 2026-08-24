import psutil

for conn in psutil.net_connections():
    if conn.laddr and conn.laddr.port in [8000, 8080]:
        print(f"Port: {conn.laddr.port} - PID: {conn.pid} - Status: {conn.status}")
