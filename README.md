# 🎮 Rock Paper Scissors Online Game

A multiplayer Rock Paper Scissors game built with Python sockets and Tkinter GUI.

## 🌟 Features

### ✅ Core Game Features
- **Multiplayer Matchmaking**: Automatic pairing of 2 players
- **Customizable Rounds**: Choose 3, 5, 7, 9, or 11 rounds
- **Rock Paper Scissors Logic**: Classic game rules
- **Real-time Score Tracking**: Live score updates
- **Replay System**: Play multiple games in sequence

### ✅ Advanced Features
- **Beautiful GUI**: Modern Tkinter interface with emojis
- **Disconnect Handling**: Graceful handling of player disconnections
- **Room Management**: Automatic room cleanup
- **Real-time Logging**: Live game log with timestamps
- **Connection Status**: Visual connection indicators

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

1. **Connect**: Enter server IP and port, click "Connect"
2. **Choose Rounds**: Player 1 selects number of rounds (3-11)
3. **Play**: Click Rock 🪨, Paper 📄, or Scissors ✂️
4. **Replay**: Choose "Yes" or "No" to play again

## 📁 Project Structure

```
rock_paper_scissors/
├── server.py          # Game server
├── room.py            # Room management logic
├── gui_client.py      # Modern GUI client
├── client.py          # Console client (legacy)
├── run_gui.py         # GUI launcher script
└── README.md          # This file
```

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
- **Multi-threaded**: Handles multiple concurrent games
- **Room-based**: Players matched into separate rooms
- **Disconnect Resilient**: Handles player disconnections gracefully

### Client Features
- **Non-blocking GUI**: Responsive interface during gameplay
- **Message Processing**: Smart message parsing for UI updates
- **Error Handling**: Robust connection error management

### Network Protocol
- **TCP Sockets**: Reliable message delivery
- **Text-based**: Human-readable message format
- **Stateful**: Server maintains game state

## 🎮 Game Flow

1. **Connection**: Players connect to server
2. **Matchmaking**: Server pairs players into rooms
3. **Round Setup**: Player 1 chooses number of rounds
4. **Gameplay**: Players make moves simultaneously
5. **Scoring**: Server calculates and broadcasts results
6. **Replay**: Option to play again with same opponent

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
