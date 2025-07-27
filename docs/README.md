# 🎮 Rock Paper Scissors Online Game

A multiplayer Rock Paper Scissors game built with Python sockets and Tkinter GUI.

## 🌟 Features

### ✅ Core Game Features

- **Multiplayer Matchmaking**: Automatic pairing of 2 players
- **Room System**: Create or join existing game rooms
- **Customizable Rounds**: Choose 3, 5, 7, 9, or 11 rounds per game
- **Rock Paper Scissors Logic**: Classic game rules with instant results
- **Real-time Score Tracking**: Live score updates throughout the match
- **Replay System**: Play multiple games in sequence with same opponent
- **Player Names**: Personalized gameplay with custom player names

### ✅ Room Management Features

- **Create Room**: Start your own room with custom name and round settings
- **Join Room**: Browse and join available rooms created by other players
- **Room List Display**: Visual list of available rooms with player count and settings
- **Double-click Join**: Quick room joining with double-click interface
- **Auto Room Cleanup**: Automatic cleanup of empty or finished rooms

### ✅ Advanced Features

- **Beautiful GUI**: Modern Tkinter interface with emojis and smooth interactions
- **Intelligent Room Browser**: Visual room list with creator info and player counts
- **Disconnect Handling**: Graceful handling of player disconnections mid-game
- **Race Condition Prevention**: Robust synchronization for simultaneous connections
- **Real-time Logging**: Live game log with timestamps and detailed information
- **Connection Status**: Visual connection indicators and status updates
- **Input Validation**: Smart input handling with error recovery

## 🚀 Quick Start

### 1. Start the Server

```bash
python server.py
```

### 2. Launch GUI Clients

```bash
python run_gui.py
```

Or directly:

```bash
python gui_client.py
```

### 3. For Console Version (Optional)

```bash
python client.py
```

## 🎯 How to Play

### 🚀 Quick Game Setup

1. **Start Server**: Run `python server.py` first
2. **Launch Clients**: Open `python gui_client.py` for each player
3. **Connect**: Enter server details and click "Connect"
4. **Enter Name**: Type your player name when prompted

### 🏠 Room System

**Option 1: Create New Room**
1. Click "🏠 Create New Room"
2. Enter a custom room name (or leave blank for default)
3. Choose number of rounds (3, 5, 7, 9, or 11)
4. Wait for another player to join

**Option 2: Join Existing Room**
1. Click "🚪 Join Existing Room"
2. Browse the list of available rooms
3. Double-click a room or select and click "Join Selected Room"
4. Game starts automatically when room is full

### 🎮 Gameplay

1. **Make Moves**: Click Rock 🪨, Paper 📄, or Scissors ✂️
2. **View Results**: See round results and running score
3. **Continue**: Play until all rounds are complete
4. **Replay Decision**: Choose "Yes" or "No" to play again with same opponent

## 🏗️ Architecture

### 📁 Project Structure
```
rock_paper_scissors/
├── server.py           # Main server with room management
├── gui_client.py       # Enhanced GUI client with room browser
├── client.py           # Simple console client for testing
├── room.py             # Room class for game logic
├── run_gui.py          # Quick launcher for GUI
├── docs/
│   └── README.md       # Project documentation
└── tests/
    ├── test_manual_debug.py     # Manual testing script
    └── test_room_functionality.py  # Room system tests
```

### 🔧 Key Components

- **Server**: Multi-threaded room management system
- **Room**: Game logic with round selection and replay
- **GUI Client**: Visual room browser and game interface
- **Player Management**: Name input and personalized experience

## 🎨 GUI Features

### 🔌 Connection Panel

- Server IP and port input
- Connection status indicator
- One-click connect/disconnect

### 📊 Game Status

- Current connection status
- Room and player information
- Real-time updates

### 🎯 Game Controls

- **Round Selection**: Radio buttons for 3/5/7/9/11 rounds
- **Move Buttons**: Large, colorful Rock/Paper/Scissors buttons
- **Replay Options**: Yes/No buttons for replay decisions

### 📝 Game Log

- Timestamped message log
- Automatic scrolling
- Real-time game updates

## 🛠️ Technical Details

### Server Architecture

- **Multi-threaded**: Handles multiple concurrent games and rooms
- **Room Management**: Dynamic room creation, joining, and cleanup
- **Player Matching**: Smart room-based player pairing system
- **Disconnect Resilient**: Handles player disconnections with opponent notification

### Client Features

- **Visual Room Browser**: Browse and join rooms with double-click
- **Enhanced GUI**: Modern interface with room management controls
- **Real-time Updates**: Live room list and game state updates
- **Smart Navigation**: Intuitive room creation and joining workflow

### Network Protocol

- **TCP Sockets**: Reliable message delivery with proper formatting
- **Room-based Messages**: Structured communication for room operations
- **State Management**: Server maintains room and player states
- **Error Recovery**: Graceful handling of connection issues

## 🎮 Game Flow

1. **Connection**: Players connect and enter their names
2. **Room Selection**: Choose to create new room or join existing
3. **Room Setup**: Creator sets room name and round count
4. **Matchmaking**: Server pairs players in selected rooms
5. **Gameplay**: Players make moves with real-time feedback
6. **Scoring**: Server calculates and broadcasts round results
7. **Replay**: Both players decide on replay with same opponent

## 🔧 Configuration

### Default Settings

- **Server**: 127.0.0.1:65433
- **Default Rounds**: 3
- **Max Players per Room**: 2

### Customization

- Change `HOST` and `PORT` in `server.py`
- Modify default rounds in GUI
- Adjust GUI colors in `gui_client.py`

## 🚨 Troubleshooting

### Connection Issues

- Ensure server is running first
- Check firewall settings
- Verify IP and port are correct

### GUI Issues

- Ensure Tkinter is installed
- Try console client as fallback
- Check Python version (3.6+)

## 📊 Game Statistics

The server logs detailed game information:

- Player connections/disconnections
- Room creation and cleanup
- Round-by-round results
- Replay decisions

## 🎉 Enjoy Playing!

Have fun playing Rock Paper Scissors with friends! The GUI makes it easy and enjoyable for players of all ages.
