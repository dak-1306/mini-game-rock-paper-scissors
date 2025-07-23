import socket
import threading
from room import Room

HOST = '127.0.0.1'
PORT = 65433  # Thay đổi port để tránh xung đột

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Cho phép tái sử dụng port
server.bind((HOST, PORT))
server.listen()

rooms = []  # Danh sách các phòng hiện tại
room_id = 1
lock = threading.Lock()

def handle_client(conn, addr):
    global room_id
    print(f"[+] New connection from {addr}")

    try:
        with lock:
            # Tìm phòng có 1 người đang chờ (không đang trong game)
            target_room = None
            for room in rooms:
                if room.is_waiting():
                    target_room = room
                    break

            # Nếu không có, tạo phòng mới
            if not target_room:
                target_room = Room(room_id)
                rooms.append(target_room)
                room_id += 1

            # Thêm client vào phòng
            player_id = target_room.add_player(conn)
            
            # Nếu là người chơi đầu tiên, yêu cầu chọn số vòng
            if player_id == 1:
                conn.sendall(f"Welcome! You are Player {player_id} in Room {target_room.room_id}\nPlease choose number of rounds (3, 5, 7, or any odd number): ".encode())
                try:
                    rounds_choice = conn.recv(1024).decode().strip()
                    rounds = int(rounds_choice)
                    if rounds <= 0 or rounds % 2 == 0:
                        conn.sendall("Invalid choice. Setting to default 3 rounds.".encode())
                        rounds = 3
                    target_room.set_total_rounds(rounds)
                    conn.sendall(f"Great! Game will be {rounds} rounds. Waiting for another player...".encode())
                except:
                    target_room.set_total_rounds(3)
                    conn.sendall("Invalid input. Set to default 3 rounds. Waiting for another player...".encode())
            else:
                conn.sendall(f"You are Player {player_id} in Room {target_room.room_id}\nGame will be {target_room.total_rounds} rounds. Starting game...".encode())

            # Nếu đủ 2 người thì bắt đầu
            if target_room.is_full():
                threading.Thread(target=target_room.run_game).start()
                
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        # Dọn dẹp phòng rỗng
        cleanup_empty_rooms()

def cleanup_empty_rooms():
    """Dọn dẹp các phòng rỗng hoặc đã kết thúc"""
    global rooms
    # Tạm thời vô hiệu hóa cleanup để tránh gây lỗi
    pass

def main():
    print("[*] Server started.")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
