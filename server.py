import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

clients = []
choices = {}
lock = threading.Lock()

def handle_client(conn, addr, player_id):
    print(f"[+] Player {player_id} connected from {addr}")
    conn.sendall(f"You are Player {player_id}".encode())

    while True:
        try:
            conn.sendall("Your move (rock/paper/scissors): ".encode())
            data = conn.recv(1024).decode().strip().lower()
            if data not in ['rock', 'paper', 'scissors']:
                conn.sendall("Invalid move. Try again.".encode())
                continue

            with lock:
                choices[player_id] = data
                print(f"[INFO] Player {player_id} chose {data}")

            # Chờ cả 2 người chơi gửi lựa chọn
            while len(choices) < 2:
                pass

            p1, p2 = choices[1], choices[2]
            result = determine_winner(p1, p2)

            if result == 0:
                conn.sendall("Result: Draw!".encode())
            elif result == player_id:
                conn.sendall("Result: You win!".encode())
            else:
                conn.sendall("Result: You lose.".encode())

            with lock:
                choices.clear()  # reset cho vòng chơi tiếp theo

        except:
            break

    conn.close()

def determine_winner(p1, p2):
    if p1 == p2:
        return 0
    elif (p1 == 'rock' and p2 == 'scissors') or \
         (p1 == 'scissors' and p2 == 'paper') or \
         (p1 == 'paper' and p2 == 'rock'):
        return 1
    else:
        return 2

def main():
    print("[*] Server started. Waiting for 2 players...")
    for player_id in [1, 2]:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
        thread.start()

if __name__ == "__main__":
    main()
