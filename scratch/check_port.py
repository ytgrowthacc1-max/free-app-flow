import socket

def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex((host, port)) == 0

is_open = check_port("127.0.0.1", 8080)
print(f"Port 8080 running: {is_open}")
