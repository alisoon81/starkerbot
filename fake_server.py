import socket
import os

def start_fake_server():
    port = int(os.environ.get("PORT", 3000))  # پورت رو از ENV بگیر
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(1)
    print(f"🚀 Fake server is listening on port {port}")
    while True:
        conn, addr = s.accept()
        conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nBot is running.")
        conn.close()
