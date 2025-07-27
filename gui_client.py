import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import time

class RockPaperScissorsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Rock Paper Scissors Game")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')
        
        # Game variables
        self.client = None
        self.connected = False
        self.player_id = None
        self.room_id = None
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🎮 Rock Paper Scissors Online",
            font=('Arial', 24, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Connection frame
        self.setup_connection_frame(main_frame)
        
        # Game status frame
        self.setup_status_frame(main_frame)
        
        # Game controls frame
        self.setup_game_frame(main_frame)
        
        # Chat/Log frame
        self.setup_log_frame(main_frame)
        
    def setup_connection_frame(self, parent):
        conn_frame = tk.LabelFrame(
            parent,
            text="🌐 Connection",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            bd=2
        )
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server input
        input_frame = tk.Frame(conn_frame, bg='#34495e')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Server:", font=('Arial', 10), fg='#ecf0f1', bg='#34495e').pack(side=tk.LEFT)
        self.host_entry = tk.Entry(input_frame, font=('Arial', 10))
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        tk.Label(input_frame, text="Port:", font=('Arial', 10), fg='#ecf0f1', bg='#34495e').pack(side=tk.LEFT)
        self.port_entry = tk.Entry(input_frame, font=('Arial', 10), width=8)
        self.port_entry.insert(0, "65433")
        self.port_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Connect button
        self.connect_btn = tk.Button(
            input_frame,
            text="🔌 Connect",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            command=self.connect_to_server,
            padx=20
        )
        self.connect_btn.pack(side=tk.RIGHT)
        
        # Player name input (initially hidden)
        self.name_frame = tk.Frame(conn_frame, bg='#34495e')
        
        tk.Label(
            self.name_frame, 
            text="Enter your name:", 
            font=('Arial', 10, 'bold'), 
            fg='#ecf0f1', 
            bg='#34495e'
        ).pack(pady=5)
        
        name_input_frame = tk.Frame(self.name_frame, bg='#34495e')
        name_input_frame.pack(pady=5)
        
        self.name_entry = tk.Entry(
            name_input_frame, 
            font=('Arial', 12), 
            width=20
        )
        self.name_entry.pack(side=tk.LEFT, padx=5)
        self.name_entry.bind('<Return>', lambda event: self.submit_name())
        
        self.submit_name_btn = tk.Button(
            name_input_frame,
            text="✅ Submit",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            command=self.submit_name
        )
        self.submit_name_btn.pack(side=tk.LEFT, padx=5)
        
        # Room choice frame (initially hidden)
        self.room_choice_frame = tk.Frame(conn_frame, bg='#34495e')
        
        choice_label = tk.Label(
            self.room_choice_frame,
            text="What would you like to do?",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        choice_label.pack(pady=10)
        
        choice_buttons_frame = tk.Frame(self.room_choice_frame, bg='#34495e')
        choice_buttons_frame.pack(pady=5)
        
        self.create_room_btn = tk.Button(
            choice_buttons_frame,
            text="🏠 Create New Room",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            width=18,
            command=lambda: self.send_choice('1')
        )
        self.create_room_btn.pack(side=tk.LEFT, padx=10)
        
        self.join_room_btn = tk.Button(
            choice_buttons_frame,
            text="🚪 Join Existing Room",
            font=('Arial', 11, 'bold'),
            bg='#9b59b6',
            fg='white',
            width=18,
            command=lambda: self.send_choice('2')
        )
        self.join_room_btn.pack(side=tk.LEFT, padx=10)
        
        # Room name input frame (initially hidden)
        self.room_name_frame = tk.Frame(conn_frame, bg='#34495e')
        
        tk.Label(
            self.room_name_frame,
            text="Enter room name:",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(pady=5)
        
        room_name_input_frame = tk.Frame(self.room_name_frame, bg='#34495e')
        room_name_input_frame.pack(pady=5)
        
        self.room_name_entry = tk.Entry(
            room_name_input_frame,
            font=('Arial', 12),
            width=20
        )
        self.room_name_entry.pack(side=tk.LEFT, padx=5)
        self.room_name_entry.bind('<Return>', lambda event: self.submit_room_name())
        
        self.submit_room_name_btn = tk.Button(
            room_name_input_frame,
            text="✅ Create Room",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            command=self.submit_room_name
        )
        self.submit_room_name_btn.pack(side=tk.LEFT, padx=5)
        
        # Room list frame (initially hidden)
        self.room_list_frame = tk.Frame(conn_frame, bg='#34495e')
        
        tk.Label(
            self.room_list_frame,
            text="🏠 Available Rooms - Click to Join",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(pady=5)
        
        # Instructions
        instructions = tk.Label(
            self.room_list_frame,
            text="💡 Double-click a room to join, or select and click 'Join Selected Room'",
            font=('Arial', 9),
            fg='#bdc3c7',
            bg='#34495e'
        )
        instructions.pack(pady=(0, 5))
        
        # Scrollable listbox for rooms
        room_list_container = tk.Frame(self.room_list_frame, bg='#34495e')
        room_list_container.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.room_listbox = tk.Listbox(
            room_list_container,
            font=('Consolas', 10),  # Monospace for better alignment
            height=6,
            bg='#2c3e50',
            fg='#ecf0f1',
            selectbackground='#3498db',
            selectforeground='#ffffff',
            activestyle='dotbox',
            bd=0,
            highlightthickness=0
        )
        self.room_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Bind double-click to join room
        self.room_listbox.bind('<Double-Button-1>', lambda e: self.join_selected_room())
        
        room_scrollbar = tk.Scrollbar(room_list_container, bg='#34495e')
        room_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))
        
        self.room_listbox.config(yscrollcommand=room_scrollbar.set)
        room_scrollbar.config(command=self.room_listbox.yview)
        
        # Button frame
        button_frame = tk.Frame(self.room_list_frame, bg='#34495e')
        button_frame.pack(pady=10)
        
        self.join_selected_room_btn = tk.Button(
            button_frame,
            text="🚪 Join Selected Room",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            command=self.join_selected_room,
            padx=20,
            pady=5,
            relief='flat',
            bd=0
        )
        self.join_selected_room_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_rooms_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            command=self.refresh_room_list,
            padx=20,
            pady=5,
            relief='flat',
            bd=0
        )
        self.refresh_rooms_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_status_frame(self, parent):
        status_frame = tk.LabelFrame(
            parent,
            text="📊 Game Status",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            bd=2
        )
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status labels
        info_frame = tk.Frame(status_frame, bg='#34495e')
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            info_frame,
            text="Status: Disconnected",
            font=('Arial', 11),
            fg='#e74c3c',
            bg='#34495e'
        )
        self.status_label.pack(anchor=tk.W)
        
        self.room_label = tk.Label(
            info_frame,
            text="Room: Not joined",
            font=('Arial', 11),
            fg='#ecf0f1',
            bg='#34495e'
        )
        self.room_label.pack(anchor=tk.W)
        
    def setup_game_frame(self, parent):
        game_frame = tk.LabelFrame(
            parent,
            text="🎯 Game Controls",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            bd=2
        )
        game_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Rounds selection (initially hidden)
        self.rounds_frame = tk.Frame(game_frame, bg='#34495e')
        
        rounds_label = tk.Label(
            self.rounds_frame,
            text="Choose number of rounds:",
            font=('Arial', 11),
            fg='#ecf0f1',
            bg='#34495e'
        )
        rounds_label.pack(pady=5)
        
        rounds_options_frame = tk.Frame(self.rounds_frame, bg='#34495e')
        rounds_options_frame.pack(pady=5)
        
        self.rounds_var = tk.StringVar(value="3")
        for rounds in ["3", "5", "7", "9", "11"]:
            tk.Radiobutton(
                rounds_options_frame,
                text=f"{rounds} rounds",
                variable=self.rounds_var,
                value=rounds,
                font=('Arial', 10),
                fg='#ecf0f1',
                bg='#34495e',
                selectcolor='#2c3e50'
            ).pack(side=tk.LEFT, padx=5)
        
        self.submit_rounds_btn = tk.Button(
            self.rounds_frame,
            text="✅ Confirm Rounds",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            command=self.submit_rounds
        )
        self.submit_rounds_btn.pack(pady=5)
        
        # Game moves (initially hidden)
        self.moves_frame = tk.Frame(game_frame, bg='#34495e')
        
        moves_label = tk.Label(
            self.moves_frame,
            text="Choose your move:",
            font=('Arial', 14, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        moves_label.pack(pady=10)
        
        # Move buttons with emojis
        moves_buttons_frame = tk.Frame(self.moves_frame, bg='#34495e')
        moves_buttons_frame.pack(pady=10)
        
        self.rock_btn = tk.Button(
            moves_buttons_frame,
            text="🪨\nRock",
            font=('Arial', 12, 'bold'),
            bg='#95a5a6',
            fg='white',
            width=8,
            height=3,
            command=lambda: self.make_move('rock')
        )
        self.rock_btn.pack(side=tk.LEFT, padx=10)
        
        self.paper_btn = tk.Button(
            moves_buttons_frame,
            text="📄\nPaper",
            font=('Arial', 12, 'bold'),
            bg='#f39c12',
            fg='white',
            width=8,
            height=3,
            command=lambda: self.make_move('paper')
        )
        self.paper_btn.pack(side=tk.LEFT, padx=10)
        
        self.scissors_btn = tk.Button(
            moves_buttons_frame,
            text="✂️\nScissors",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=8,
            height=3,
            command=lambda: self.make_move('scissors')
        )
        self.scissors_btn.pack(side=tk.LEFT, padx=10)
        
        # Replay frame (initially hidden)
        self.replay_frame = tk.Frame(game_frame, bg='#34495e')
        
        replay_label = tk.Label(
            self.replay_frame,
            text="Do you want to play again?",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        replay_label.pack(pady=10)
        
        replay_buttons_frame = tk.Frame(self.replay_frame, bg='#34495e')
        replay_buttons_frame.pack(pady=5)
        
        self.yes_btn = tk.Button(
            replay_buttons_frame,
            text="✅ Yes",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=10,
            command=lambda: self.replay_response('yes')
        )
        self.yes_btn.pack(side=tk.LEFT, padx=10)
        
        self.no_btn = tk.Button(
            replay_buttons_frame,
            text="❌ No",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=10,
            command=lambda: self.replay_response('no')
        )
        self.no_btn.pack(side=tk.LEFT, padx=10)
        
        # Initially hide all game frames
        self.hide_all_game_frames()
        self.name_frame.pack_forget()  # Hide name input initially
        self.room_choice_frame.pack_forget()  # Hide room choice initially
        self.room_name_frame.pack_forget()  # Hide room name input initially
        self.room_list_frame.pack_forget()  # Hide room list initially
        
    def setup_log_frame(self, parent):
        log_frame = tk.LabelFrame(
            parent,
            text="📝 Game Log",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            bd=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=('Consolas', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#ecf0f1'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def hide_all_game_frames(self):
        self.rounds_frame.pack_forget()
        self.moves_frame.pack_forget()
        self.replay_frame.pack_forget()
        
    def show_name_input(self):
        self.name_frame.pack(fill=tk.X, padx=10, pady=10)
        self.name_entry.focus()
        
    def hide_name_input(self):
        self.name_frame.pack_forget()
        
    def show_room_choice(self):
        self.room_choice_frame.pack(fill=tk.X, padx=10, pady=10)
        
    def hide_room_choice(self):
        self.room_choice_frame.pack_forget()
        
    def show_room_name_input(self):
        self.hide_room_choice()
        self.room_name_frame.pack(fill=tk.X, padx=10, pady=10)
        self.room_name_entry.focus()
        
    def hide_room_name_input(self):
        self.room_name_frame.pack_forget()
        
    def show_room_list(self):
        self.hide_room_choice()
        self.room_list_frame.pack(fill=tk.X, padx=10, pady=10)
        
    def hide_room_list(self):
        self.room_list_frame.pack_forget()
        
    def show_rounds_selection(self):
        self.hide_all_game_frames()
        self.rounds_frame.pack(fill=tk.X, padx=10, pady=10)
        
    def show_moves_selection(self):
        self.hide_all_game_frames()
        self.moves_frame.pack(fill=tk.X, padx=10, pady=10)
        
    def show_replay_selection(self):
        self.hide_all_game_frames()
        self.replay_frame.pack(fill=tk.X, padx=10, pady=10)
        
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def connect_to_server(self):
        if self.connected:
            return
            
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            self.connected = True
            
            self.status_label.config(text="Status: Connected", fg='#27ae60')
            self.connect_btn.config(text="🔌 Connected", state='disabled', bg='#95a5a6')
            
            self.log(f"🔌 Connected to {host}:{port}")
            
            # Start receiving messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.log(f"❌ Connection failed: {e}")
            
    def receive_messages(self):
        while self.connected:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                    
                self.process_message(data)
                
            except Exception as e:
                if self.connected:
                    self.log(f"❌ Error receiving message: {e}")
                break
                
        self.disconnect()
        
    def process_message(self, message):
        """Process incoming messages and update GUI accordingly"""
        self.log(f"📨 {message}")
        
        # Show name input when server asks for name
        if "Please enter your name:" in message:
            self.root.after(0, self.show_name_input)
            return
            
        # Show room choice when server asks for choice
        if "What would you like to do?" in message and "1. Create" in message:
            self.root.after(0, self.show_room_choice)
            return
            
        # Show room name input when server asks for room name
        if "Enter room name:" in message:
            self.root.after(0, self.show_room_name_input)
            return
            
        # Process room list when server sends available rooms
        if "Available Rooms:" in message and "Enter room number" in message:
            self.root.after(0, lambda: self.process_room_list(message))
            return
            
        # Handle "No available rooms" message
        if "No available rooms" in message:
            self.root.after(0, self.show_room_name_input)
            return
        
        # Extract player and room info
        if "You are Player" in message and "Room" in message:
            parts = message.split()
            for i, part in enumerate(parts):
                if part == "Player":
                    self.player_id = parts[i + 1]
                if part == "Room":
                    self.room_id = parts[i + 1]
            self.room_label.config(text=f"Room: {self.room_id} | Player: {self.player_id}")
            
        # Show rounds selection for player 1
        if "Please choose number of rounds" in message:
            self.root.after(0, self.show_rounds_selection)
            
        # Show moves selection when round starts
        if "Your move (rock/paper/scissors)" in message:
            self.root.after(0, self.show_moves_selection)
            
        # Show replay selection
        if "Do you want to play again?" in message:
            self.root.after(0, self.show_replay_selection)
            
        # Hide game frames when game ends
        if "Thanks for playing" in message or "Goodbye" in message:
            self.root.after(0, self.hide_all_game_frames)
            self.root.after(1000, self.disconnect)
            
    def submit_name(self):
        if self.connected and self.client:
            name = self.name_entry.get().strip()
            if name:
                self.client.sendall((name + "\n").encode())
                self.log(f"📤 Sent name: {name}")
                self.hide_name_input()
            else:
                messagebox.showwarning("Invalid Name", "Please enter a valid name!")
                
    def send_choice(self, choice):
        if self.connected and self.client:
            self.client.sendall((choice + "\n").encode())
            if choice == "1":
                self.log(f"📤 Selected: Create new room")
            else:
                self.log(f"📤 Selected: Join existing room")
            self.hide_room_choice()
            
    def submit_room_name(self):
        if self.connected and self.client:
            room_name = self.room_name_entry.get().strip()
            if room_name:
                self.client.sendall((room_name + "\n").encode())
                self.log(f"📤 Creating room: {room_name}")
                self.hide_room_name_input()
            else:
                # Send empty string to use default name
                self.client.sendall("\n".encode())
                self.log(f"📤 Creating room with default name")
                self.hide_room_name_input()
                
    def process_room_list(self, message):
        # Clear existing items
        self.room_listbox.delete(0, tk.END)
        
        # Parse room list from message
        lines = message.split('\n')
        self.available_rooms = []  # Store room info for joining
        
        for line in lines:
            line = line.strip()
            # Look for numbered room entries like "1. TestRoom (by Dang) - 1/2 players - 3 rounds"
            if line and line[0].isdigit() and '.' in line:
                # Extract room info
                parts = line.split('.', 1)
                if len(parts) == 2:
                    room_number = parts[0].strip()
                    room_details = parts[1].strip()
                    
                    # Store room info for later use
                    self.available_rooms.append({
                        'number': int(room_number),
                        'details': room_details,
                        'full_line': line
                    })
                    
                    # Parse room details for better display
                    # Format: "TestRoom (by Dang) - 1/2 players - 3 rounds"
                    try:
                        if '(' in room_details and ')' in room_details:
                            # Extract room name and creator
                            name_part = room_details.split('(')[0].strip()
                            creator_part = room_details.split('(')[1].split(')')[0]
                            remaining = room_details.split(')', 1)[1] if ')' in room_details else ""
                            
                            # Format for display
                            display_text = f"🏠 {name_part:<15} 👤 {creator_part:<10} {remaining.strip()}"
                        else:
                            display_text = f"🏠 {room_details}"
                    except:
                        display_text = f"🏠 {room_details}"
                    
                    self.room_listbox.insert(tk.END, display_text)
                
        if self.available_rooms:
            self.show_room_list()
            self.log(f"📋 Found {len(self.available_rooms)} available rooms")
        else:
            self.log("📭 No rooms available")
            self.hide_room_list()
            
    def join_selected_room(self):
        selection = self.room_listbox.curselection()
        if selection and self.connected and self.client and hasattr(self, 'available_rooms'):
            selected_index = selection[0]
            if selected_index < len(self.available_rooms):
                room_info = self.available_rooms[selected_index]
                room_number = room_info['number']
                
                # Send room number to server
                self.client.sendall((str(room_number) + "\n").encode())
                
                selected_room_text = room_info['details']
                self.log(f"📤 Joining room: {selected_room_text}")
                self.hide_room_list()
            else:
                messagebox.showwarning("Selection Error", "Invalid room selection!")
        else:
            messagebox.showwarning("No Selection", "Please select a room to join!")
            
    def refresh_room_list(self):
        """Send request to server to get updated room list"""
        if self.connected and self.client:
            # Request fresh room list by choosing option 2 again
            self.log("🔄 Refreshing room list...")
            # This would require server-side support for refresh command
            # For now, show message to user
            messagebox.showinfo("Refresh", "To see updated rooms, please reconnect to the server.")
        else:
            messagebox.showwarning("Not Connected", "Please connect to server first!")
                
    def submit_rounds(self):
        if self.connected and self.client:
            rounds = self.rounds_var.get()
            self.client.sendall((rounds + "\n").encode())
            self.log(f"📤 Selected {rounds} rounds")
            self.hide_all_game_frames()
            
    def make_move(self, move):
        if self.connected and self.client:
            self.client.sendall((move + "\n").encode())
            self.log(f"📤 Played: {move}")
            
            # Disable move buttons temporarily
            self.rock_btn.config(state='disabled')
            self.paper_btn.config(state='disabled')
            self.scissors_btn.config(state='disabled')
            
            # Re-enable after 2 seconds
            self.root.after(2000, self.enable_move_buttons)
            
    def enable_move_buttons(self):
        self.rock_btn.config(state='normal')
        self.paper_btn.config(state='normal')
        self.scissors_btn.config(state='normal')
        
    def replay_response(self, response):
        if self.connected and self.client:
            self.client.sendall((response + "\n").encode())
            self.log(f"📤 Replay response: {response}")
            self.hide_all_game_frames()
            
    def disconnect(self):
        self.connected = False
        if self.client:
            try:
                self.client.close()
            except:
                pass
            
        self.status_label.config(text="Status: Disconnected", fg='#e74c3c')
        self.room_label.config(text="Room: Not joined")
        self.connect_btn.config(text="🔌 Connect", state='normal', bg='#27ae60')
        self.hide_all_game_frames()
        self.hide_name_input()
        self.hide_room_choice()
        self.hide_room_name_input()
        self.hide_room_list()
        self.log("🔌 Disconnected from server")
        
    def on_closing(self):
        self.disconnect()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RockPaperScissorsGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
