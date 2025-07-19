import socket
import threading
from room import Room

HOST = '127.0.0.1'
PORT = 65432

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

rooms = []  # Danh sách các phòng hiện tại
room_id = 1
lock = threading.Lock()

def handle_client(conn, addr):
    global room_id
    print(f"[+] New connection from {addr}")

    with lock:
        # Tìm phòng có 1 người đang chờ
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
        conn.sendall(f"You are Player {player_id} in Room {target_room.room_id}".encode())

        # Nếu đủ 2 người thì bắt đầu
        if target_room.is_full():
            threading.Thread(target=target_room.run_game).start()

def main():
    print("[*] Server started.")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
