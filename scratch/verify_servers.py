import socket

def test_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(('127.0.0.1', port)) == 0

print(f"Port 8080 (Main Dashboard): {'ONLINE' if test_port(8080) else 'OFFLINE'}")
print(f"Port 8085 (Campaign Dashboard): {'ONLINE' if test_port(8085) else 'OFFLINE'}")
