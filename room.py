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

    def is_waiting(self):
        return len(self.players) == 1

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
        
        # Đợi cho đến khi có số vòng được set
        while self.waiting_for_rounds:
            threading.Event().wait(0.1)
        
        # Thông báo số vòng cho cả 2 người chơi
        for pid, conn in self.players.items():
            conn.sendall(f"\nGame will be played for {self.total_rounds} rounds. Let's start!\n".encode())

        while self.round <= self.total_rounds:
            for pid, conn in self.players.items():
                conn.sendall(f"\nRound {self.round}/{self.total_rounds} - Your move (rock/paper/scissors): ".encode())

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
            result = self.determine_winner(p1, p2)

            # Gửi kết quả
            if result == 0:
                msg = "Draw!"
            elif result == 1:
                msg = "You win!" if p1 else "Invalid input."
                self.scores[1] += 1
            else:
                msg = "You win!" if p2 else "Invalid input."
                self.scores[2] += 1

            self.players[1].sendall(f"Round {self.round} result: {msg}".encode())
            self.players[2].sendall(f"Round {self.round} result: {'Draw!' if result==0 else 'You lose.' if result==1 else 'You win!'}".encode())

            self.round += 1
            self.choices.clear()

        # Kết thúc game
        self.send_final_result()

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
            if score1 == score2:
                msg = f"\nGame Over! Final Score: {score1}-{score2}. It's a draw!"
            elif (pid == 1 and score1 > score2) or (pid == 2 and score2 > score1):
                msg = f"\nGame Over! Final Score: {score1}-{score2}. 🏆 You win!"
            else:
                msg = f"\nGame Over! Final Score: {score1}-{score2}. 😢 You lose."
            conn.sendall(msg.encode())
            conn.close()
