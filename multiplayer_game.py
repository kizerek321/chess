import sys
import chess
import pygame
from drawBoard import get_promotion_choice

from drawBoard import (
    draw_board,
    draw_captured,
    draw_check,
    draw_game_over,
    draw_pending,
    draw_pieces,
    draw_valid,
    draw_waiting,
    _pixel_to_sq,
    get_promotion_choice,
    draw_opponent_disconnected
)
from constants import screen, timer, fps, font, medium_font
from game_state import GameState
from network import NetworkClient

"""
client.py — chess client for multiplayer mode.

Runs Pygame GUI and connects to the chess server.
The server is the authority on game state — the client does not move pieces
locally before receiving confirmation (move_ok).

Move flow:
  1. Click → local validation → highlight legal squares (UX)
  2. Second click on destination square → send {"type":"move","uci":"e2e4"}
  3. Wait for move_ok from the server
  4. After move_ok: rebuild board from FEN, update captured, rerender

Perspective:
  - White player: normal orientation (white pieces at the bottom)
  - Black player: board rotated (black pieces at the bottom)
"""

HOST = "127.0.0.1"
PORT = 8000

def handle_server_message(msg: dict, state: GameState) -> None:
    """
    Processes a message sent by the server and updates the game state.

    Parameters:
        msg:   dictionary with the server message
        state: current game state
    """
    msg_type = msg.get("type")

    if msg_type == "game_start":
        # Server assigned a color and sent the starting FEN
        color_str = msg["color"]
        state.my_color = chess.WHITE if color_str == "white" else chess.BLACK
        state.board = chess.Board(msg["fen"])
        state.connected = True
        print(f"[Client] Game started — you are: {color_str.upper()}")

    elif msg_type == "move_ok":
        # Server approved the move — synchronize via FEN
        state.board = chess.Board(msg["fen"])
        state.captured_pieces_white = msg.get("captured_white", [])
        state.captured_pieces_black = msg.get("captured_black", [])
        state.last_move = msg.get("last_move")
        state.pending_move = False
        state.selection = None
        state.valid_moves = []
        print(f"[Client] Move approved: {state.last_move}")

    elif msg_type == "move_rejected":
        # Server rejected the move — revert to the state before the click
        reason = msg.get("reason", "Unknown reason")
        print(f"[Client] Move rejected by server: {reason}")
        state.pending_move = False
        state.selection = None
        state.valid_moves = []

    elif msg_type == "game_over":
        # Game ended — synchronize the final state and determine the winner
        state.board = chess.Board(msg["fen"])
        state.captured_pieces_white = msg.get("captured_white", [])
        state.captured_pieces_black = msg.get("captured_black", [])
        state.last_move = msg.get("last_move")
        state.pending_move = False
        state.selection = None
        state.valid_moves = []

        result = msg.get("result", "")
        if result == "white_wins":
            state.winner = "White"
        elif result == "black_wins":
            state.winner = "Black"
        else:
            state.winner = "Draw"

        state.game_over = True
        print(f"[Client] Game over: {result} — {msg.get('reason', '')}")

    elif msg_type == "disconnected":
        print("[Client] Disconnected from server.")
        if not state.game_over:
            state.game_over = True
            state.winner = "Disconnected"

    elif msg_type == "opponent_disconnected":
        print("[Client] Opponent disconnected.")
        state.opponent_disconnected = True

    elif msg_type == "opponent_reconnected":
        print("[Client] Opponent reconnected.")
        state.opponent_disconnected = False



def handle_board_click(x_tile: int, y_tile: int, state: GameState, network: NetworkClient) -> None:
    """
    Processes a click within the 8×8 chessboard.

    Parameters:
        x_tile:  column (0-7, counted from the left in pixels / 100)
        y_tile:  row    (0-7, counted from the top in pixels / 100)
        state:   game state
        network: network connection object
    """
    flipped = (state.my_color == chess.BLACK)
    clicked_sq = _pixel_to_sq(x_tile, y_tile, flipped)

    if state.selection is None:
        # Select a piece if it belongs to the current player
        piece = state.board.piece_at(clicked_sq)
        if piece and piece.color == state.my_color and piece.color == state.board.turn:
            state.selection = clicked_sq
            state.valid_moves = [
                move.to_square
                for move in state.board.legal_moves
                if move.from_square == clicked_sq
            ]
    else:
        # Select a destination
        piece = state.board.piece_at(clicked_sq)

        if piece and piece.color == state.my_color and piece.color == state.board.turn:
            # Clicked on another own piece — change selection
            state.selection = clicked_sq
            state.valid_moves = [
                move.to_square
                for move in state.board.legal_moves
                if move.from_square == clicked_sq
            ]

        elif clicked_sq in state.valid_moves:
            # Clicked on a legal destination square — find the move and send it to the server
            move_to_send = None
            is_promotion = False
            for move in state.board.legal_moves:
                if move.from_square == state.selection and move.to_square == clicked_sq:
                    if move.promotion:
                        is_promotion = True
                        break
                    else:
                        move_to_send = move
                        break
            
            if is_promotion:
                chosen_piece = get_promotion_choice(state.my_color)
                for move in state.board.legal_moves:
                    if move.from_square == state.selection and move.to_square == clicked_sq and move.promotion == chosen_piece:
                        move_to_send = move
                        break

            if move_to_send:
                network.send_move(move_to_send.uci())
                state.pending_move = True
                # Do not move the board locally — wait for move_ok from the server
                state.selection = None
                state.valid_moves = []
        else:
            # Clicked on an empty or illegal square — deselect
            state.selection = None
            state.valid_moves = []

def client_run(host_ip: str, port: int = 8000) -> None:
    """Runs the chess client in multiplayer mode."""
    # Initialize state and connection
    state = GameState()

    print(f"[Client] Connecting to server {host_ip}:{port}...")
    try:
        network = NetworkClient(host_ip, port)
        print("[Client] Connected. Waiting for the game to start...")
    except ConnectionRefusedError:
        print(f"[Client] Could not connect to the server on {host_ip}:{port}. Is the server running?")
        sys.exit(1)

    pygame.display.set_caption("Chess — Multiplayer")
    run = True

    while run:
        timer.tick(fps)

        # Animations (blinking chess)
        if state.counter < 30:
            state.counter += 1
        else:
            state.counter = 0

        msg = network.poll()
        if msg:
            handle_server_message(msg, state)

        screen.fill('azure')
        draw_board(state)
        draw_pieces(state)
        draw_captured(state)
        draw_check(state)

        if state.selection is not None:
            draw_valid(state, state.valid_moves)

        if not state.connected:
            draw_waiting(state)
        elif state.pending_move:
            draw_pending(state)

        if state.game_over:
            draw_game_over(state)

        if state.opponent_disconnected:
            draw_opponent_disconnected(state)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            # Left mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Do not react to clicks when:
                #   - the game has ended
                #   - not connected or no color assigned
                #   - it's not our turn
                #   - waiting for server confirmation
                if (state.game_over
                        or not state.connected
                        or state.my_color is None
                        or state.board.turn != state.my_color
                        or state.pending_move
                        or state.opponent_disconnected):
                    continue

                x_coord = event.pos[0] // 100
                y_coord = event.pos[1] // 100

                # FORFEIT button (columns 8-9, row 8)
                if x_coord in (8, 9) and y_coord == 8:
                    network.send_forfeit()
                    continue

                # Click within the 8×8 board
                if x_coord < 8 and y_coord < 8:
                    handle_board_click(x_coord, y_coord, state, network)

            # Restart after the game ends (Enter)
            if event.type == pygame.KEYDOWN and state.game_over:
                if event.key == pygame.K_RETURN:
                    run = False

        pygame.display.flip()

    network.close()
    #pygame.quit()