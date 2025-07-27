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

        # Hỏi người chơi muốn tạo phòng hay tham gia phòng
        conn.sendall(f"Hello {player_name}! What would you like to do?\n1. Create a new room\n2. Join existing room\nEnter your choice (1 or 2): ".encode())
        
        choice = conn.recv(1024).decode().strip()
        
        if choice == "1":
            # Tạo phòng mới
            conn.sendall("Enter room name: ".encode())
            room_name = conn.recv(1024).decode().strip()
            if not room_name:
                room_name = f"{player_name}'s Room"
            
            with lock:
                target_room = Room(room_id, room_name, player_name)
                rooms.append(target_room)
                room_id += 1
            
            # Thêm người tạo vào phòng
            player_id = target_room.add_player(conn, player_name)
            conn.sendall(f"Room '{room_name}' created! You are Player {player_id} in Room {target_room.room_id}\nPlease choose number of rounds (3, 5, 7, or any odd number): ".encode())
            
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
                
        elif choice == "2":
            # Tham gia phòng có sẵn
            available_rooms = []
            with lock:
                for room in rooms:
                    if room.is_waiting():  # Chỉ hiển thị phòng đang chờ
                        available_rooms.append(room)
            
            if not available_rooms:
                conn.sendall("No available rooms. Creating a new room for you...\n".encode())
                with lock:
                    target_room = Room(room_id, f"{player_name}'s Room", player_name)
                    rooms.append(target_room)
                    room_id += 1
                
                player_id = target_room.add_player(conn, player_name)
                conn.sendall(f"Room created! You are Player {player_id} in Room {target_room.room_id}\nPlease choose number of rounds (3, 5, 7, or any odd number): ".encode())
                
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
                # Hiển thị danh sách phòng
                room_list = "Available Rooms:\n"
                for i, room in enumerate(available_rooms):
                    room_info = room.get_room_info()
                    room_list += f"{i+1}. {room_info['name']} (by {room_info['creator']}) - {room_info['players']}/{room_info['max_players']} players - {room_info['rounds']} rounds\n"
                room_list += "Enter room number (1, 2, 3...) or room name to join: "
                conn.sendall(room_list.encode())
                
                try:
                    room_choice_input = conn.recv(1024).decode().strip()
                    print(f"[+] Player {player_name} chose room input: '{room_choice_input}'")
                    
                    # Thử parse số thứ tự trước
                    try:
                        room_choice = int(room_choice_input) - 1
                        print(f"[+] Parsed as room index: {room_choice}")
                        if 0 <= room_choice < len(available_rooms):
                            target_room = available_rooms[room_choice]
                            print(f"[+] Found target room: {target_room.room_name}")
                        else:
                            conn.sendall("Invalid room number. Disconnecting...\n".encode())
                            return
                    except ValueError:
                        print(f"[+] Not a number, trying room name match")
                        # Nếu không phải số, thử tìm theo tên phòng
                        target_room = None
                        for room in available_rooms:
                            if room.room_name.lower() == room_choice_input.lower():
                                target_room = room
                                break
                        
                        if not target_room:
                            conn.sendall("Room not found. Disconnecting...\n".encode())
                            return
                    
                    # Đợi cho player 1 set số vòng trước
                    print(f"[+] Waiting for room {target_room.room_id} rounds to be set...")
                    while target_room.waiting_for_rounds:
                        threading.Event().wait(0.1)
                    
                    print(f"[+] Adding {player_name} to room {target_room.room_id}")
                    player_id = target_room.add_player(conn, player_name)
                    other_player_name = target_room.get_player_name(1)
                    conn.sendall(f"Joined '{target_room.room_name}'! You are Player {player_id}\nYou will play against {other_player_name}. Game will be {target_room.total_rounds} rounds. Starting game...\n".encode())
                    
                    # Bắt đầu game khi đủ 2 người
                    if target_room.is_full():
                        print(f"[Room {target_room.room_id}] Both players ready: {target_room.get_player_name(1)} vs {target_room.get_player_name(2)}")
                        
                        if not target_room.game_in_progress:
                            print(f"[+] Starting game for room {target_room.room_id}")
                            threading.Thread(target=target_room.run_game).start()
                        return
                except Exception as e:
                    print(f"Error joining room for {player_name}: {e}")
                    conn.sendall("Invalid input. Disconnecting...\n".encode())
                    return
        else:
            conn.sendall("Invalid choice. Disconnecting...\n".encode())
            return

        # Chờ người chơi thứ 2 nếu là người tạo phòng
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
