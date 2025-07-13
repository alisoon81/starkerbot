import socket

def start_fake_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 8080))  # پورت مورد نیاز Render
    s.listen(1)
    print("Fake server is running on port 8080...")
    while True:
        conn, addr = s.accept()
        conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nBot is running.")
        conn.close()
