import threading

class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}  # {1: conn1, 2: conn2}
        self.choices = {}
        self.scores = {1: 0, 2: 0}
        self.round = 1
        self.total_rounds = None  # Sẽ được set khi người chơi đầu tiên chọn
        self.lock = threading.Lock()
        self.waiting_for_rounds = True  # Đợi người chơi đầu tiên chọn số vòng
        self.game_in_progress = False  # Đánh dấu game đang diễn ra

    def is_waiting(self):
        return len(self.players) == 1 and not self.game_in_progress

    def is_full(self):
        return len(self.players) == 2

    def add_player(self, conn):
        player_id = 1 if 1 not in self.players else 2
        self.players[player_id] = conn
        return player_id

    def set_total_rounds(self, rounds):
        """Set số vòng chơi cho phòng"""
        self.total_rounds = rounds
        self.waiting_for_rounds = False

    def run_game(self):
        print(f"[Room {self.room_id}] Game started with 2 players.")
        self.game_in_progress = True  # Đánh dấu game đang diễn ra
        
        # Đợi cho đến khi có số vòng được set
        while self.waiting_for_rounds:
            threading.Event().wait(0.1)
        
        # Vòng lặp chính cho việc chơi lại
        replay_count = 0
        while True:
            replay_count += 1
            print(f"[Room {self.room_id}] Starting game round {replay_count}")
            
            # Thông báo số vòng cho cả 2 người chơi
            for pid, conn in self.players.items():
                try:
                    conn.sendall(f"\nGame will be played for {self.total_rounds} rounds. Let's start!\n".encode())
                    print(f"[Room {self.room_id}] Sent start message to Player {pid}")
                except Exception as e:
                    print(f"[Room {self.room_id}] Error sending start message to Player {pid}: {e}")
                    self.game_in_progress = False
                    return  # Nếu không gửi được thì thoát

            # Chơi game
            print(f"[Room {self.room_id}] Starting rounds...")
            self.play_rounds()
            
            # Gửi kết quả cuối game
            print(f"[Room {self.room_id}] Sending final result...")
            self.send_final_result()
            
            # Hỏi chơi lại và xử lý kết quả
            print(f"[Room {self.room_id}] Handling replay...")
            if not self.handle_replay():
                print(f"[Room {self.room_id}] Game ended, no replay")
                self.game_in_progress = False
                break  # Thoát nếu không chơi lại
            else:
                print(f"[Room {self.room_id}] Replay agreed, continuing...")

    def play_rounds(self):
        """Chơi các vòng của game"""
        while self.round <= self.total_rounds:
            for pid, conn in self.players.items():
                try:
                    conn.sendall(f"\nRound {self.round}/{self.total_rounds} - Your move (rock/paper/scissors): ".encode())
                except:
                    return

            for pid, conn in self.players.items():
                try:
                    move = conn.recv(1024).decode().strip().lower()
                    if move not in ['rock', 'paper', 'scissors']:
                        conn.sendall("Invalid move. You lose this round.".encode())
                        move = None
                    with self.lock:
                        self.choices[pid] = move
                except:
                    self.choices[pid] = None

            # Xử lý kết quả
            p1, p2 = self.choices.get(1), self.choices.get(2)
            print(f"[Room {self.room_id}] Round {self.round}: P1={p1}, P2={p2}")
            result = self.determine_winner(p1, p2)
            print(f"[Room {self.room_id}] Winner: {result}")

            # Gửi kết quả
            if result == 0:
                msg_p1 = "Draw!"
                msg_p2 = "Draw!"
            elif result == 1:
                msg_p1 = "You win!" if p1 and p1 in ['rock', 'paper', 'scissors'] else "Invalid input."
                msg_p2 = "You lose." if p2 and p2 in ['rock', 'paper', 'scissors'] else "Other player won."
                self.scores[1] += 1
            else:  # result == 2
                msg_p1 = "You lose." if p1 and p1 in ['rock', 'paper', 'scissors'] else "Other player won."
                msg_p2 = "You win!" if p2 and p2 in ['rock', 'paper', 'scissors'] else "Invalid input."
                self.scores[2] += 1

            try:
                self.players[1].sendall(f"Round {self.round} result: {msg_p1}".encode())
                self.players[2].sendall(f"Round {self.round} result: {msg_p2}".encode())
                print(f"[Room {self.room_id}] Sent results: P1='{msg_p1}', P2='{msg_p2}'")
            except:
                return

            self.round += 1
            self.choices.clear()

    def determine_winner(self, p1, p2):
        if p1 == p2:
            return 0
        elif (p1 == 'rock' and p2 == 'scissors') or \
             (p1 == 'scissors' and p2 == 'paper') or \
             (p1 == 'paper' and p2 == 'rock'):
            return 1
        else:
            return 2

    def send_final_result(self):
        score1, score2 = self.scores[1], self.scores[2]
        for pid, conn in self.players.items():
            try:
                if score1 == score2:
                    msg = f"\nGame Over! Final Score: {score1}-{score2}. It's a draw!"
                elif (pid == 1 and score1 > score2) or (pid == 2 and score2 > score1):
                    msg = f"\nGame Over! Final Score: {score1}-{score2}. 🏆 You win!"
                else:
                    msg = f"\nGame Over! Final Score: {score1}-{score2}. 😢 You lose."
                conn.sendall(msg.encode())
            except:
                pass

    def handle_replay(self):
        """Xử lý việc hỏi chơi lại. Trả về True nếu chơi lại, False nếu không"""
        replay_responses = {}
        
        print(f"[Room {self.room_id}] Asking players for replay...")
        
        # Gửi câu hỏi cho cả 2 người chơi
        for pid, conn in self.players.items():
            try:
                conn.sendall("\nDo you want to play again? (yes/no): ".encode())
                print(f"[Room {self.room_id}] Asked Player {pid} for replay")
            except Exception as e:
                print(f"[Room {self.room_id}] Error asking Player {pid}: {e}")
                replay_responses[pid] = False
                continue
        
        # Nhận phản hồi từ cả 2 người chơi
        for pid, conn in self.players.items():
            try:
                print(f"[Room {self.room_id}] Waiting for Player {pid} response...")
                response = conn.recv(1024).decode().strip().lower()
                print(f"[Room {self.room_id}] Player {pid} responded: {response}")
                replay_responses[pid] = response in ['yes', 'y', '1']
            except Exception as e:
                print(f"[Room {self.room_id}] Error receiving from Player {pid}: {e}")
                replay_responses[pid] = False
        
        print(f"[Room {self.room_id}] Replay responses: {replay_responses}")
        
        # Kiểm tra nếu cả 2 đều đồng ý
        if len(replay_responses) == 2 and all(replay_responses.values()):
            # Reset game và chơi lại
            print(f"[Room {self.room_id}] Both players agreed to replay!")
            self.reset_game()
            for pid, conn in self.players.items():
                try:
                    conn.sendall("Both players agreed! Starting new game...\n".encode())
                    print(f"[Room {self.room_id}] Sent replay confirmation to Player {pid}")
                except Exception as e:
                    print(f"[Room {self.room_id}] Error sending confirmation to Player {pid}: {e}")
                    return False
            return True  # Chơi lại
        else:
            # Kết thúc và đóng kết nối
            print(f"[Room {self.room_id}] Not all players agreed, ending game...")
            for pid, conn in self.players.items():
                try:
                    if pid not in replay_responses or not replay_responses[pid]:
                        conn.sendall("Thanks for playing! Goodbye!\n".encode())
                    else:
                        conn.sendall("Other player declined. Thanks for playing! Goodbye!\n".encode())
                    conn.close()
                except Exception as e:
                    print(f"[Room {self.room_id}] Error closing connection for Player {pid}: {e}")
            return False  # Không chơi lại

    def reset_game(self):
        """Reset trạng thái game để chơi lại"""
        self.scores = {1: 0, 2: 0}
        self.round = 1
        self.choices.clear()
        # Không reset game_in_progress ở đây vì vẫn đang chơi
