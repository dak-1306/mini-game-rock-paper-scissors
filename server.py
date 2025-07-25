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
    target_room = None
    player_id = None
    player_name = None

    try:
        # Yêu cầu nhập tên người chơi
        conn.sendall("🎮 Welcome to Rock Paper Scissors! 🎮\nPlease enter your name: ".encode())
        try:
            player_name = conn.recv(1024).decode().strip()
            if not player_name:
                player_name = f"Player_{addr[1]}"  # Sử dụng port làm tên mặc định
        except Exception as e:
            print(f"Error receiving player name from {addr}: {e}")
            player_name = f"Player_{addr[1]}"

        print(f"[+] Player '{player_name}' connected from {addr}")

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

        # Thêm client vào phòng với tên (ngoài lock để tránh deadlock)
        player_id = target_room.add_player(conn, player_name)
        
        # Nếu là người chơi đầu tiên, yêu cầu chọn số vòng
        if player_id == 1:
            conn.sendall(f"Welcome {player_name}! You are Player {player_id} in Room {target_room.room_id}\nPlease choose number of rounds (3, 5, 7, or any odd number): ".encode())
            try:
                rounds_choice = conn.recv(1024).decode().strip()
                rounds = int(rounds_choice)
                if rounds <= 0 or rounds % 2 == 0:
                    conn.sendall("Invalid choice. Setting to default 3 rounds.\n".encode())
                    rounds = 3
                target_room.set_total_rounds(rounds)
                conn.sendall(f"Great! Game will be {rounds} rounds. Waiting for another player...\n".encode())
            except Exception as e:
                print(f"Error setting rounds for {player_name}: {e}")
                target_room.set_total_rounds(3)
                conn.sendall("Invalid input. Set to default 3 rounds. Waiting for another player...\n".encode())
        else:
            # Đợi cho player 1 set số vòng trước
            while target_room.waiting_for_rounds:
                threading.Event().wait(0.1)
            
            other_player_name = target_room.get_player_name(1)
            conn.sendall(f"Welcome {player_name}! You are Player {player_id} in Room {target_room.room_id}\nYou will play against {other_player_name}. Game will be {target_room.total_rounds} rounds. Starting game...\n".encode())

            # Nếu đủ 2 người thì bắt đầu (chỉ player 2 mới trigger game start)
            if target_room.is_full():
                print(f"[Room {target_room.room_id}] Both players ready: {target_room.get_player_name(1)} vs {target_room.get_player_name(2)}")
                
                # Chỉ bắt đầu game nếu chưa có game nào đang chạy
                if not target_room.game_in_progress:
                    threading.Thread(target=target_room.run_game).start()
                # Không cleanup ngay lập tức khi game vừa bắt đầu
                return

        # Nếu chỉ có 1 người (Player 1) thì chờ
        if not target_room.is_full():
            print(f"[Room {target_room.room_id}] Waiting for second player. Current: {player_name}")
            
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
        # Xử lý disconnect
        if target_room and player_id:
            target_room.handle_disconnect(player_id)
    finally:
        # Chỉ cleanup khi có lỗi hoặc khi game chưa bắt đầu
        if not (target_room and target_room.is_full() and target_room.game_in_progress):
            cleanup_empty_rooms()

def cleanup_empty_rooms():
    """Dọn dẹp các phòng rỗng hoặc đã kết thúc"""
    global rooms
    with lock:
        active_rooms = []
        for room in rooms:
            should_keep = False
            
            # Giữ phòng nếu đang có game trong progress
            if room.game_in_progress and len(room.players) > 0:
                should_keep = True
            # Giữ phòng nếu có 1 player đang chờ (chưa trong game)
            elif len(room.players) == 1 and not room.game_in_progress:
                should_keep = True
            # Giữ phòng nếu có 2 players (dù chưa bắt đầu game)
            elif len(room.players) == 2:
                should_keep = True
            
            if should_keep:
                active_rooms.append(room)
            else:
                # Phòng thực sự rỗng hoặc đã kết thúc hoàn toàn
                print(f"[Cleanup] Removing empty room {room.room_id}")
                # Đóng tất cả connections còn lại trong phòng
                for pid, conn in list(room.players.items()):
                    try:
                        conn.close()
                    except:
                        pass
        
        rooms = active_rooms
        print(f"[Cleanup] Active rooms: {len(rooms)}")

def main():
    print("[*] Server started.")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
