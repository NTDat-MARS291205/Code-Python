import socket

HOST, PORT = "127.0.0.1", 12000

with socket.create_connection((HOST, PORT), timeout=5) as s:
    msg = input("Nhập chuỗi thường: ").encode()
    s.sendall(msg)
    data = s.recv(1024)
    print("Server trả về:", data.decode())
