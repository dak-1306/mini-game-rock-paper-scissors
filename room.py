import threading

class Room:
    def __init__(self, room_id, room_name="Room", creator_name="Unknown"):
        self.room_id = room_id
        self.room_name = room_name
        self.creator_name = creator_name
        self.players = {}  # {1: conn1, 2: conn2}
        self.player_names = {}  # {1: name1, 2: name2}
        self.choices = {}
        self.scores = {1: 0, 2: 0}
        self.round = 1
        self.total_rounds = None  # Sẽ được set khi người chơi đầu tiên chọn
        self.lock = threading.Lock()
        self.waiting_for_rounds = True  # Đợi người chơi đầu tiên chọn số vòng
        self.game_in_progress = False  # Đánh dấu game đang diễn ra
        self.active_players = set()  # Theo dõi players còn kết nối

    def is_waiting(self):
        return len(self.players) == 1 and not self.game_in_progress

    def is_full(self):
        return len(self.players) == 2
    
    def get_room_info(self):
        """Trả về thông tin phòng để hiển thị trong danh sách"""
        return {
            "id": self.room_id,
            "name": self.room_name,
            "creator": self.creator_name,
            "players": len(self.players),
            "max_players": 2,
            "rounds": self.total_rounds if self.total_rounds else "TBD",
            "status": "In Game" if self.game_in_progress else "Waiting"
        }

    def add_player(self, conn, name="Unknown"):
        player_id = 1 if 1 not in self.players else 2
        self.players[player_id] = conn
        self.player_names[player_id] = name
        self.active_players.add(player_id)
        return player_id

    def get_player_name(self, player_id):
        return self.player_names.get(player_id, f"Player {player_id}")

    def remove_player(self, player_id):
        """Remove player khi disconnect"""
        if player_id in self.players:
            try:
                self.players[player_id].close()
            except:
                pass
            del self.players[player_id]
        if player_id in self.player_names:
            del self.player_names[player_id]
        self.active_players.discard(player_id)
        print(f"[Room {self.room_id}] {self.get_player_name(player_id)} disconnected")

    def check_connection(self, player_id):
        """Kiểm tra kết nối của player"""
        if player_id not in self.players:
            return False
        try:
            conn = self.players[player_id]
            # Thử gửi 1 byte để test connection
            original_timeout = conn.gettimeout()
            conn.settimeout(0.1)
            conn.send(b'')
            conn.settimeout(original_timeout)
            return True
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            # Connection đã đóng
            return False
        except Exception as e:
            # Các lỗi khác, coi như connection vẫn OK
            print(f"[Room {self.room_id}] Connection check warning for Player {player_id}: {e}")
            return True
        finally:
            try:
                conn.settimeout(original_timeout)
            except:
                pass

    def handle_disconnect(self, disconnected_player_id):
        """Xử lý khi có player disconnect"""
        disconnected_name = self.get_player_name(disconnected_player_id)
        print(f"[Room {self.room_id}] Handling disconnect for {disconnected_name}")
        
        # Remove player bị disconnect
        self.remove_player(disconnected_player_id)
        
        # Thông báo cho player còn lại
        remaining_player_id = 2 if disconnected_player_id == 1 else 1
        if remaining_player_id in self.players:
            remaining_name = self.get_player_name(remaining_player_id)
            try:
                self.players[remaining_player_id].sendall(
                    f"\n{disconnected_name} has disconnected. You win by default!\nThanks for playing! Goodbye!\n".encode()
                )
                self.players[remaining_player_id].close()
            except:
                pass
            self.remove_player(remaining_player_id)
        
        # Đánh dấu game kết thúc
        self.game_in_progress = False
        return True  # Phòng cần được dọn dẹp

    def set_total_rounds(self, rounds):
        """Set số vòng chơi cho phòng"""
        self.total_rounds = rounds
        self.waiting_for_rounds = False

    def run_game(self):
        # Kiểm tra nếu game đã bắt đầu rồi thì return
        if self.game_in_progress:
            print(f"[Room {self.room_id}] Game already in progress, skipping duplicate start")
            return
            
        # Đánh dấu game đang diễn ra ngay từ đầu
        self.game_in_progress = True
        
        player1_name = self.get_player_name(1)
        player2_name = self.get_player_name(2)
        print(f"[Room {self.room_id}] Game started: {player1_name} vs {player2_name}")
        
        # Đợi cho đến khi có số vòng được set
        while self.waiting_for_rounds:
            threading.Event().wait(0.1)
        
        # Thêm delay nhỏ để đảm bảo welcome messages được gửi trước
        threading.Event().wait(0.2)
        
        # Vòng lặp chính cho việc chơi lại
        replay_count = 0
        while True:
            replay_count += 1
            print(f"[Room {self.room_id}] Starting game round {replay_count}")
            
            # Thông báo số vòng cho cả 2 người chơi
            for pid, conn in self.players.items():
                try:
                    opponent_name = self.get_player_name(2 if pid == 1 else 1)
                    conn.sendall(f"\n🎮 Match {replay_count}: You vs {opponent_name}\nGame will be played for {self.total_rounds} rounds. Let's start!\n".encode())
                    print(f"[Room {self.room_id}] Sent start message to {self.get_player_name(pid)}")
                except Exception as e:
                    print(f"[Room {self.room_id}] Error sending start message to {self.get_player_name(pid)}: {e}")
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
            # Kiểm tra kết nối trước khi gửi prompt
            disconnected_players = []
            for pid in list(self.players.keys()):
                if not self.check_connection(pid):
                    disconnected_players.append(pid)
            
            if disconnected_players:
                for pid in disconnected_players:
                    if self.handle_disconnect(pid):
                        return  # Phòng cần dọn dẹp
            
            # Gửi prompt cho players còn lại
            for pid, conn in self.players.items():
                try:
                    conn.sendall(f"\nRound {self.round}/{self.total_rounds} - Your move (rock/paper/scissors): ".encode())
                except Exception as e:
                    print(f"[Room {self.room_id}] Error sending prompt to Player {pid}: {e}")
                    if self.handle_disconnect(pid):
                        return

            # Nhận moves từ players
            for pid, conn in self.players.items():
                try:
                    move = conn.recv(1024).decode().strip().lower()
                    if move not in ['rock', 'paper', 'scissors']:
                        conn.sendall("Invalid move. You lose this round.\n".encode())
                        move = None
                    with self.lock:
                        self.choices[pid] = move
                except Exception as e:
                    print(f"[Room {self.room_id}] Error receiving move from Player {pid}: {e}")
                    if self.handle_disconnect(pid):
                        return
                    self.choices[pid] = None

            # Kiểm tra nếu còn đủ players để tiếp tục
            if len(self.players) < 2:
                print(f"[Room {self.room_id}] Not enough players to continue")
                return

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
        player1_name = self.get_player_name(1)
        player2_name = self.get_player_name(2)
        
        for pid, conn in self.players.items():
            try:
                opponent_name = player2_name if pid == 1 else player1_name
                your_score = score1 if pid == 1 else score2
                opponent_score = score2 if pid == 1 else score1
                
                if score1 == score2:
                    msg = f"\n🎮 Game Over! Final Score: You {your_score} - {opponent_score} {opponent_name}\n🤝 It's a draw!"
                elif (pid == 1 and score1 > score2) or (pid == 2 and score2 > score1):
                    msg = f"\n🎮 Game Over! Final Score: You {your_score} - {opponent_score} {opponent_name}\n🏆 You win!"
                else:
                    msg = f"\n🎮 Game Over! Final Score: You {your_score} - {opponent_score} {opponent_name}\n😢 You lose."
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
        for pid, conn in list(self.players.items()):
            if pid not in self.players:  # Player đã disconnect
                replay_responses[pid] = False
                continue
                
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
            for pid, conn in list(self.players.items()):
                try:
                    if pid not in replay_responses or not replay_responses[pid]:
                        conn.sendall("Thanks for playing! Goodbye!\n".encode())
                    else:
                        conn.sendall("Other player declined. Thanks for playing! Goodbye!\n".encode())
                except Exception as e:
                    print(f"[Room {self.room_id}] Error sending goodbye to Player {pid}: {e}")
                
                try:
                    conn.close()
                except Exception as e:
                    print(f"[Room {self.room_id}] Error closing connection for Player {pid}: {e}")
                    
            # Clear players dict
            self.players.clear()
            self.player_names.clear()
            self.active_players.clear()
            return False  # Không chơi lại

    def reset_game(self):
        """Reset trạng thái game để chơi lại"""
        self.scores = {1: 0, 2: 0}
        self.round = 1
        self.choices.clear()
        # Không reset game_in_progress ở đây vì vẫn đang chơi
