import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
    msg = input("Nhập chuỗi thường: ").encode()
    client.sendto(msg, (SERVER_HOST, SERVER_PORT))
    data, _ = client.recvfrom(2048)
    print("Server trả về:", data.decode())
