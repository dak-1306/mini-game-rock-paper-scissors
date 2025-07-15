import socket           # Thư viện socket để tạo server
import threading        # Thư viện xử lý nhiều client cùng lúc

HOST = '127.0.0.1'      # IP localhost (chạy trên cùng máy)
PORT = 65432            # Cổng giao tiếp

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Tạo socket TCP
server.bind((HOST, PORT))  # Gắn IP và cổng vào server
server.listen(2)           # Lắng nghe tối đa 2 client

clients = []               # Danh sách các client kết nối
choices = {}               # Lưu lựa chọn của từng người chơi
lock = threading.Lock()    # Khóa để tránh 2 luồng ghi cùng lúc

# Xử lý 1 client
def handle_client(conn, addr, player_id):
    print(f"[+] Player {player_id} connected from {addr}")
    conn.sendall(f"You are Player {player_id}".encode())

    while True:
        try:
            # Gửi yêu cầu nhập nước đi
            conn.sendall("Your move (rock/paper/scissors): ".encode())
            data = conn.recv(1024).decode().strip().lower()

            # Kiểm tra hợp lệ
            if data not in ['rock', 'paper', 'scissors']:
                conn.sendall("Invalid move. Try again.".encode())
                continue

            # Lưu lựa chọn vào từ điển
            with lock:
                choices[player_id] = data
                print(f"[INFO] Player {player_id} chose {data}")

            # Đợi đến khi đủ 2 người chơi
            while len(choices) < 2:
                pass

            # Lấy lựa chọn 2 người và tính kết quả
            p1, p2 = choices[1], choices[2]
            result = determine_winner(p1, p2)

            # Gửi kết quả về client
            if result == 0:
                conn.sendall("Result: Draw!".encode())
            elif result == player_id:
                conn.sendall("Result: You win!".encode())
            else:
                conn.sendall("Result: You lose.".encode())

            # Reset choices cho vòng sau
            with lock:
                choices.clear()

        except:
            break

    conn.close()

# Hàm so sánh lựa chọn để xác định người thắng
def determine_winner(p1, p2):
    if p1 == p2:
        return 0
    elif (p1 == 'rock' and p2 == 'scissors') or \
         (p1 == 'scissors' and p2 == 'paper') or \
         (p1 == 'paper' and p2 == 'rock'):
        return 1
    else:
        return 2

# Hàm main chạy server
def main():
    print("[*] Server started. Waiting for 2 players...")
    for player_id in [1, 2]:
        conn, addr = server.accept()                        # Nhận kết nối client
        clients.append(conn)                                # Lưu vào danh sách
        thread = threading.Thread(target=handle_client,     # Tạo luồng xử lý
                                  args=(conn, addr, player_id))
        thread.start()

if __name__ == "__main__":
    main()
