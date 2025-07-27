import socket
import time

def test_manual():
    """Test thủ công để debug"""
    print("=== Testing Room Creation and Joining ===")
    
    # Test Player 1 - Tạo phòng
    print("\n--- Player 1: Creating Room ---")
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 65434))
    
    # Nhận welcome
    data = sock1.recv(1024).decode()
    print("P1:", data.replace('\n', '\\n'))
    
    # Gửi tên
    sock1.sendall("Dang\n".encode())
    
    # Nhận menu
    data = sock1.recv(1024).decode()
    print("P1:", data.replace('\n', '\\n'))
    
    # Chọn create room
    sock1.sendall("1\n".encode())
    
    # Nhận room name prompt
    data = sock1.recv(1024).decode()
    print("P1:", data.replace('\n', '\\n'))
    
    # Gửi room name
    sock1.sendall("TestRoom\n".encode())
    
    # Nhận rounds prompt
    data = sock1.recv(1024).decode()
    print("P1:", data.replace('\n', '\\n'))
    
    # Gửi rounds
    sock1.sendall("3\n".encode())
    
    # Nhận confirmation
    data = sock1.recv(1024).decode()
    print("P1:", data.replace('\n', '\\n'))
    
    print("\n--- Player 2: Joining Room ---")
    time.sleep(1)  # Đợi P1 setup xong
    
    # Test Player 2 - Join phòng
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 65434))
    
    # Nhận welcome
    data = sock2.recv(1024).decode()
    print("P2:", data.replace('\n', '\\n'))
    
    # Gửi tên
    sock2.sendall("Hao\n".encode())
    
    # Nhận menu
    data = sock2.recv(1024).decode()
    print("P2:", data.replace('\n', '\\n'))
    
    # Chọn join room
    sock2.sendall("2\n".encode())
    
    # Nhận room list
    data = sock2.recv(1024).decode()
    print("P2:", data.replace('\n', '\\n'))
    
    # Chọn room 1
    sock2.sendall("1\n".encode())
    
    # Nhận join confirmation
    try:
        data = sock2.recv(1024).decode()
        print("P2:", data.replace('\n', '\\n'))
        print("\n✅ JOIN SUCCESS!")
    except Exception as e:
        print(f"P2 Error: {e}")
    
    time.sleep(2)
    sock1.close()
    sock2.close()

if __name__ == "__main__":
    test_manual()
