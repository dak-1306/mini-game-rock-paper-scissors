import socket  # Thư viện socket

HOST = '127.0.0.1'  # IP server
PORT = 65432        # Cổng server

# Tạo socket TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))  # Kết nối đến server

welcome = client.recv(1024).decode()  # Nhận thông báo Player 1/2
print(welcome)

# Vòng lặp chơi game
while True:
    try:
        prompt = client.recv(1024).decode()  # Nhận lời nhắc nhập nước đi hoặc kết quả
        print(prompt)

        # Nếu kết thúc game thì thoát vòng lặp
        if "Game Over" in prompt:
            break

        move = input(">> ").strip()          # Nhập nước đi từ bàn phím
        client.sendall(move.encode())        # Gửi về server

        result = client.recv(1024).decode()  # Nhận kết quả vòng chơi
        print(result)

    except:
        break  # Nếu lỗi thì thoát game

client.close()  # Đóng kết nối sau khi kết thúc
