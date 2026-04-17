# Python Multiplayer Chess Game
*CREATED DURING CONCURRENT AND DISTRIBUTED PROCESSING COURSE AT GDANSK UNIVERSITY OF TECHNOLOGY*

A fully functional chess game built in Python using `pygame` for the graphical user interface and `python-chess` for move validation and game logic. 

## Features
- **Local Play:** Play hot-seat multiplayer on a single machine.
- **Online Multiplayer:** Client-server architecture to play across different machines.
  - Centralized server acts as the source of truth for move validation.
  - Automatic board flipping depending on the player's color.
  - Synchronization of game state using FEN (Forsyth-Edwards Notation).
- **GUI:** Highlights legal moves, displays captured pieces, and detects check/checkmate/draw mathematically.

## Setup
1. Create a virtual environment: `conda create --name chess`
2. Activate the virtual environment: `conda activate chess`
3. Install the required packages: `pip install chess pygame`

## How to Play

### Local Mode (Single Machine)
Run the local hot-seat mode where both players take turns on the same screen:
```bash
python main.py
```

### Multiplayer Mode (Client-Server)
To play across different windows or machines via TCP/IP sockets:

1. **Start the server:** 
   ```bash
   python server.py
   ```
   The server will bind to `127.0.0.1:8000` by default and wait for two clients to connect.

2. **Start the first client (White):**
   ```bash
   python client.py
   ```

3. **Start the second client (Black):**
   Open another terminal and run:
   ```bash
   python client.py
   ```

Once both clients connect, the server will assign colors and start the game.

## Project Structure
- `main.py` - Entry point for local hot-seat game.
- `client.py` - Pygame client that connects to the server for multiplayer mode.
- `server.py` - Authoritative server that handles connections, game state, and move validation.
- `network.py` & `protocol.py` - Custom TCP socket networking and JSON message framing.
- `game_state.py` - Core state representation and wrapper for `python-chess`.
- `drawBoard.py` - Pygame rendering logic.
- `constants.py` - Configuration, fonts, and dimensions.