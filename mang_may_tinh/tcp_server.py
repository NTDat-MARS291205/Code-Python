import socket

HOST = "0.0.0.0"
PORT = 12000
BACKLOG = 5

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(BACKLOG)
    print(f"[TCP] Server sẵn sàng trên {HOST}:{PORT}")

    while True:
        conn, addr = srv.accept()
        print("🌐 Kết nối từ", addr)
        with conn:
            # Đọc 1 thông điệp (đến khi client đóng hoặc xuống dòng)
            buf = conn.recv(1024)
            if not buf:
                continue
            conn.sendall(buf.upper())
        print("✋ Đóng kết nối", addr)
