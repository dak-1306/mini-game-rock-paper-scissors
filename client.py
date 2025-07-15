import socket  # Thư viện socket để kết nối tới server

HOST = '127.0.0.1'  # IP server (ở đây là cùng máy)
PORT = 65432        # Cổng kết nối

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Tạo socket TCP
client.connect((HOST, PORT))                                # Kết nối đến server

# Nhận lời chào từ server (Bạn là Player 1 hoặc 2)
welcome = client.recv(1024).decode()
print(welcome)

while True:
    prompt = client.recv(1024).decode()  # Nhận yêu cầu nhập nước đi
    print(prompt)

    move = input(">> ").strip()          # Nhập lựa chọn từ bàn phím
    client.sendall(move.encode())        # Gửi lên server

    result = client.recv(1024).decode()  # Nhận kết quả từ server
    print(result)
