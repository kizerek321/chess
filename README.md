# Python Multiplayer Chess Game
*CREATED DURING CONCURRENT AND DISTRIBUTED PROCESSING COURSE AT GDANSK UNIVERSITY OF TECHNOLOGY*

A fully functional chess game built in Python using `pygame` for the graphical user interface and `python-chess` for move validation and game logic. The project features both local and networked multiplayer modes, utilizing a client-server architecture with UDP LAN discovery for seamless matchmaking.

## Features
- **Two Game Modes:** 
  - **Local Play:** Play hot-seat multiplayer on a single machine.
  - **LAN Multiplayer:** Play across different machines on the same network using a robust client-server model.
- **Server Browser (LAN Discovery):** Clients can automatically discover active game servers on the local network via UDP broadcasts, displaying available rooms and player counts.
- **Multi-room Server Manager:** The central server dynamically creates multiple game "rooms" on separate TCP ports, allowing several concurrent games.
- **Authoritative Server:** The server acts as the absolute source of truth for move validation, preventing cheating. Clients only render moves once approved by the server.
- **Dynamic Board Orientation:** Automatically flips the board for the black player to ensure an intuitive perspective for both sides.
- **State Synchronization:** Fast and reliable synchronization using FEN (Forsyth-Edwards Notation) and JSON message framing.
- **Advanced Chess Logic:** Highlights legal moves, displays captured pieces, handles pawn promotion, and detects check, checkmate, stalemate, insufficient material, and repetitive draws.

## Setup
1. Create a virtual environment: `conda create --name chess`
2. Activate the virtual environment: `conda activate chess`
3. Install the required packages: `pip install chess pygame`

## How to Play

### Recommended Flow (GUI Menu)
The easiest way to play is through the graphical menu, which allows you to seamlessly launch a local game or connect to an existing LAN server.

1. **Start the GUI Menu:**
   ```bash
   python menu.py
   ```
2. Choose between **Local Game** or **Browse Servers (LAN)**.

### Setting up a Multiplayer Server
To host games for players on your local network:

1. **Start the Server Manager:**
   ```bash
   python ServerManager.py
   ```
2. The server manager will launch and automatically create the first game room. It continuously broadcasts its presence over UDP (port 8001).
3. From the server manager console, you can type `add room` to spin up additional parallel games, or `exit` to cleanly shut down all rooms.
4. Players running `menu.py` on the same network will automatically see your available rooms under the "Browse Servers" tab and can click to connect.

### Manual Connection (Alternative)
If you wish to bypass the GUI menu or play across non-LAN networks, you can run `multiplayer_game.py` directly to connect to a specific server and port.

## Project Structure
- `menu.py` - Graphical main menu with UDP server discovery and mode selection.
- `ServerManager.py` - Central server application managing multiple game rooms and LAN broadcasting.
- `chessRoom.py` - Handles the game logic and socket communication for an individual multiplayer room instance.
- `multiplayer_game.py` - Pygame client for multiplayer mode, connecting to a `ChessRoom` to render state and forward inputs.
- `local_game.py` - Core logic for the local hot-seat game loop.
- `network.py` & `protocol.py` - Custom TCP socket networking and JSON message framing for client-server communication.
- `game_state.py` - Core state representation and wrapper for `python-chess`.
- `drawBoard.py` - Pygame rendering logic for drawing the board, pieces, valid moves, and GUI elements.
- `constants.py` - Configuration, fonts, dimensions, and visual tokens.