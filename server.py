import socket
import threading

# Cấu hình địa chỉ IP và cổng
HOST = '127.0.0.1'
PORT = 65432

# Tạo socket TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))   # Gán địa chỉ và cổng
server.listen(2)            # Lắng nghe 2 client

# Các biến toàn cục
clients = []                        # Danh sách kết nối client
choices = {}                        # Lưu lựa chọn của từng player
scores = {1: 0, 2: 0}               # Điểm số của 2 player
lock = threading.Lock()            # Dùng để đồng bộ luồng
total_rounds = 3                   # Tổng số vòng chơi
round_number = 1                   # Vòng hiện tại
ready = {1: False, 2: False}       # Trạng thái đã chọn xong trong vòng
next_round_ready = {1: False, 2: False}  # Trạng thái sẵn sàng vòng mới
game_over = False                  # Cờ kết thúc game

# Hàm xác định người thắng dựa trên luật oẳn tù tì
def determine_winner(p1, p2):
    if p1 == p2:
        return 0  # Hòa
    elif (p1 == 'rock' and p2 == 'scissors') or \
         (p1 == 'scissors' and p2 == 'paper') or \
         (p1 == 'paper' and p2 == 'rock'):
        return 1  # Player 1 thắng
    else:
        return 2  # Player 2 thắng

# Xử lý client riêng biệt
def handle_client(conn, addr, player_id):
    print(f"[+] Player {player_id} connected from {addr}")
    conn.sendall(f"You are Player {player_id}".encode())

    global round_number, game_over

    # Đánh dấu client đã sẵn sàng vòng đầu
    with lock:
        next_round_ready[player_id] = True

    while True:
        # Nếu đã hết game thì thoát
        with lock:
            if game_over:
                break

        # Đợi cả 2 client sẵn sàng để bắt đầu vòng
        while True:
            with lock:
                if game_over:
                    break
                if next_round_ready[1] and next_round_ready[2]:
                    break
        if game_over:
            break

        try:
            # Gửi yêu cầu nhập lựa chọn
            conn.sendall(f"\nRound {round_number}/{total_rounds} - Your move (rock/paper/scissors): ".encode())
            data = conn.recv(1024).decode().strip().lower()

            # Kiểm tra hợp lệ
            if data not in ['rock', 'paper', 'scissors']:
                conn.sendall("Invalid move. Try again.".encode())
                continue

            # Lưu lựa chọn
            with lock:
                choices[player_id] = data
                print(f"[Round {round_number}] Player {player_id} chose {data}")
                ready[player_id] = True

            # Đợi cả 2 player nhập xong
            while True:
                with lock:
                    if game_over:
                        break
                    if ready[1] and ready[2]:
                        break
            if game_over:
                break

            # Khi cả 2 đã chọn -> xử lý kết quả
            with lock:
                p1, p2 = choices[1], choices[2]
                result = determine_winner(p1, p2)

                if result == 0:
                    conn.sendall(f"Round {round_number} Result: Draw!".encode())
                elif result == player_id:
                    conn.sendall(f"Round {round_number} Result: You win!".encode())
                    scores[player_id] += 1
                else:
                    conn.sendall(f"Round {round_number} Result: You lose.".encode())

                # Đánh dấu client đã xong vòng hiện tại
                next_round_ready[player_id] = False

            # Khi cả 2 client đã xong vòng, chuẩn bị vòng tiếp theo
            with lock:
                if not next_round_ready[1] and not next_round_ready[2]:
                    choices.clear()
                    ready[1] = ready[2] = False
                    round_number += 1

                    if round_number > total_rounds:
                        game_over = True
                    else:
                        next_round_ready[1] = True
                        next_round_ready[2] = True

        except:
            break

    # Khi kết thúc game -> gửi kết quả cuối cùng cho client
    with lock:
        final_score = scores[player_id]
        opponent_score = scores[3 - player_id]

    if final_score > opponent_score:
        final_result = "🏆 You are the overall winner!"
    elif final_score < opponent_score:
        final_result = "😢 You lost the game."
    else:
        final_result = "🤝 It's a tie overall!"

    conn.sendall(f"\nGame Over! Final score: You {final_score} - Opponent {opponent_score}\n{final_result}".encode())
    conn.close()

# Hàm khởi động server
def main():
    print("[*] Server started. Waiting for 2 players...")
    for player_id in [1, 2]:
        conn, addr = server.accept()
        clients.append(conn)
        # Tạo luồng xử lý riêng cho mỗi client
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
        thread.start()

if __name__ == "__main__":
    main()
