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
2. The server manager will launch and begin broadcasting over UDP (port 8001). It features **dynamic room allocation**—it automatically spins up new parallel game rooms (TCP servers) whenever existing ones fill up, ensuring there is always an open room for new players.
3. Players running `menu.py` on the same network will automatically see your available rooms under the "Browse Servers" tab and can click to connect.
4. From the server manager console, you can type `exit` to cleanly shut down the server and gracefully close all active rooms.

### Manual Connection (Alternative)
If you wish to bypass the GUI menu or play across non-LAN networks, you can run `multiplayer_game.py` directly to connect to a specific server and port.

## Project Structure
- `menu.py` - The entry point of the application. Displays the graphical main menu, allows mode selection, and runs a background thread for UDP server discovery (LAN).
- `ServerManager.py` - The central server manager. Automatically spawns new game rooms to ensure there is always a free spot for incoming players. Broadcasts available rooms on the local network via UDP.
- `chessRoom.py` - Represents a single multiplayer game session (room) operating on its own TCP port. Handles move validation, server-side game state, and notifies clients about moves, game overs, or player disconnects.
- `multiplayer_game.py` - The client-side Pygame interface for multiplayer matches. Sends user interactions to the `ChessRoom` server, waits for the server to approve moves, and renders the synchronized game state.
- `local_game.py` - The Pygame interface and game loop for the local "hot-seat" mode, where both players play on the same physical screen.
- `network.py` - Contains the `NetworkClient` class, managing the asynchronous TCP connection with the server and polling messages via a thread-safe queue.
- `protocol.py` - Utility functions (`send_msg`, `recv_msg`) that enforce the communication protocol, structuring messages as prefixed-length JSON payloads to prevent TCP stream fragmentation.
- `game_state.py` - Maintains the client-side UI state and integrates with the `python-chess` library to compute legal moves, manage the board state, and track captured pieces.
- `drawBoard.py` - Centralizes the Pygame rendering logic. Responsible for drawing the board, chess pieces, visual highlights (valid moves, checks), and UI overlays.
- `constants.py` - Stores global configuration values such as screen dimensions, FPS limits, colors, and font settings.