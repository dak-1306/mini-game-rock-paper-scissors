import socket
import sys
import threading

class RockPaperScissorsClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def receive_messages(self):
        while self.running:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                print(data)
                if "Game Over" in data:
                    self.running = False
            except:
                break

    def connect(self, host, port):
        try:
            self.client.connect((host, port))
            
            # Luồng nhận tin nhắn
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # Gửi input
            while self.running:
                user_input = input()
                if not self.running:
                    break
                self.client.sendall(user_input.encode())
                
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.client.close()
            print("Disconnected from server")

if __name__ == "__main__":
    HOST = '127.0.0.1' if len(sys.argv) < 2 else sys.argv[1]
    PORT = 65432 if len(sys.argv) < 3 else int(sys.argv[2])
    
    game_client = RockPaperScissorsClient()
    game_client.connect(HOST, PORT)