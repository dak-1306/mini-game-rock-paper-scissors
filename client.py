import socket

HOST = '127.0.0.1'
PORT = 65432

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Nhận thông báo ban đầu
welcome = client.recv(1024).decode()
print(welcome)

while True:
    prompt = client.recv(1024).decode()
    print(prompt)

    move = input(">> ").strip()
    client.sendall(move.encode())

    result = client.recv(1024).decode()
    print(result)
