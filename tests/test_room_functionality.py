import socket
import threading
import time

def test_player_1():
    """Test player 1 tạo phòng"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 65433))
    
    # Nhận welcome message
    data = sock.recv(1024).decode()
    print("P1 received:", data)
    
    # Gửi tên
    sock.sendall("Dang\n".encode())
    
    # Nhận menu
    data = sock.recv(1024).decode()
    print("P1 received:", data)
    
    # Chọn tạo phòng
    sock.sendall("1\n".encode())
    
    # Nhận yêu cầu room name
    data = sock.recv(1024).decode()
    print("P1 received:", data)
    
    # Gửi room name
    sock.sendall("TestRoom\n".encode())
    
    # Nhận yêu cầu rounds
    data = sock.recv(1024).decode()
    print("P1 received:", data)
    
    # Gửi rounds
    sock.sendall("3\n".encode())
    
    # Nhận confirmation
    data = sock.recv(1024).decode()
    print("P1 received:", data)
    
    # Giữ kết nối
    time.sleep(10)
    sock.close()

def test_player_2():
    """Test player 2 tham gia phòng"""
    time.sleep(2)  # Đợi player 1 tạo phòng
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 65433))
    
    # Nhận welcome message
    data = sock.recv(1024).decode()
    print("P2 received:", data)
    
    # Gửi tên
    sock.sendall("Hao\n".encode())
    
    # Nhận menu
    data = sock.recv(1024).decode()
    print("P2 received:", data)
    
    # Chọn join phòng
    sock.sendall("2\n".encode())
    
    # Nhận danh sách phòng
    data = sock.recv(1024).decode()
    print("P2 received:", data)
    
    # Gửi room choice
    sock.sendall("1\n".encode())  # Chọn phòng đầu tiên
    
    # Nhận confirmation
    try:
        data = sock.recv(1024).decode()
        print("P2 received:", data)
    except Exception as e:
        print("P2 error:", e)
    
    time.sleep(5)
    sock.close()

if __name__ == "__main__":
    # Chạy cả 2 player
    t1 = threading.Thread(target=test_player_1)
    t2 = threading.Thread(target=test_player_2)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
