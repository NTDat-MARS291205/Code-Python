import socket

HOST = "0.0.0.0"
PORT = 12000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((HOST, PORT))
    print(f"[UDP] Server sẵn sàng trên {HOST}:{PORT}")
    while True:
        data, client_addr = server.recvfrom(2048)
        print(f"↩ from {client_addr}: {data!r}")
        server.sendto(data.upper(), client_addr)
