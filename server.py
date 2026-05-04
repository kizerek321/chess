import socket
import threading
import chess
import json
import time
from protocol import send_msg, recv_msg

HOST = "0.0.0.0"
#PORT = 8000


class ChessServer:
    """
    Class to handle rooms for chess players.
    Currently:
    - Server waits for two clients
    - Assigns them colors (white/black)a
    - Verifies every move (is it legal on the authoritative board)
    - After accepting the move, sends the new FEN to both players
    - Tracks captured pieces and detects the end of the game
    """
    def __init__(self):
        # Authoritative chess board of the server
        self.board = chess.Board()

        # Two client sockets: index 0 = white, 1 = black
        self.clients: list[socket.socket | None] = [None, None]
        self.colors = ["white", "black"]

        # Mutex protecting board modifications
        self.lock = threading.Lock()

        # Lists of piece types (int 1-6) of captured pieces
        self.captured_white: list[int] = []   # pieces captured by white
        self.captured_black: list[int] = []   # pieces captured by black

        self.game_over = False

    def _broadcast(self, msg: dict) -> None:
        """Sends a message to both connected clients."""
        for conn in self.clients:
            if conn:
                try:
                    send_msg(conn, msg)
                except Exception:
                    pass

    def _send_to(self, player_idx: int, msg: dict) -> None:
        """Sends a message to a single player."""
        conn = self.clients[player_idx]
        if conn:
            try:
                send_msg(conn, msg)
            except Exception:
                pass

    def _build_state_msg(self, last_move_uci: str | None) -> dict:
        """Builds a move_ok message with the current board state."""
        return {
            "type": "move_ok",
            "fen": self.board.fen(),
            "last_move": last_move_uci,
            "captured_white": self.captured_white[:],
            "captured_black": self.captured_black[:],
        }

    def _end_game(self, result: str, reason: str, last_move_uci: str | None) -> None:
        """Sends a game_over message to both players and sets the game over flag."""
        self.game_over = True
        msg = {
            "type": "game_over",
            "fen": self.board.fen(),
            "result": result,
            "reason": reason,
            "last_move": last_move_uci,
            "captured_white": self.captured_white[:],
            "captured_black": self.captured_black[:],
        }
        self._broadcast(msg)

    def handle_client(self, conn: socket.socket, player_idx: int) -> None:
        """Main loop for handling a single client."""
        color = self.colors[player_idx]
        client_chess_color = chess.WHITE if color == "white" else chess.BLACK
        sock_file = conn.makefile("r", encoding="utf-8")

        try:
            while not self.game_over:
                msg = recv_msg(sock_file)
                if msg is None:
                    # Client disconnected
                    print(f"[Server] Player {color} disconnected.")
                    break

                if msg["type"] == "move":
                    self._handle_move(msg, player_idx, client_chess_color, color)

                elif msg["type"] == "forfeit":
                    with self.lock:
                        winner = "black" if color == "white" else "white"
                        print(f"[Server] Player {color} resigned.")
                        self._end_game(f"{winner}_wins", "forfeit", None)

        except Exception as e:
            print(f"[Server] Error handling client {color}: {e}")
        finally:
            conn.close()

    def _handle_move(
        self,
        msg: dict,
        player_idx: int,
        client_chess_color: chess.Color,
        color: str,
    ) -> None:
        """Verifies and executes a move sent by the client."""
        with self.lock:
            if self.game_over:
                return

            # Check if it's this player's turn
            if self.board.turn != client_chess_color:
                self._send_to(player_idx, {
                    "type": "move_rejected",
                    "reason": "Not your turn",
                })
                return

            # Parse UCI
            try:
                move = chess.Move.from_uci(msg["uci"])
            except (ValueError, KeyError):
                self._send_to(player_idx, {
                    "type": "move_rejected",
                    "reason": "Invalid UCI format",
                })
                return

            # Check legality
            if move not in self.board.legal_moves:
                self._send_to(player_idx, {
                    "type": "move_rejected",
                    "reason": "Illegal move",
                })
                print(f"[Server] Illegal move from {color}: {msg['uci']}")
                return

            # Track captured pieces before executing the move
            if self.board.is_en_passant(move):
                captured_type = chess.PAWN
            else:
                target = self.board.piece_at(move.to_square)
                captured_type = target.piece_type if target else None

            if captured_type:
                if self.board.turn == chess.WHITE:
                    self.captured_white.append(captured_type)
                else:
                    self.captured_black.append(captured_type)

            # Execute the move
            self.board.push(move)
            print(f"[Server] Move {color}: {msg['uci']} — FEN: {self.board.fen()}")

            # Check for game end
            if self.board.is_checkmate():
                winner = "white" if self.board.turn == chess.BLACK else "black"
                self._end_game(f"{winner}_wins", "checkmate", msg["uci"])
            elif self.board.is_stalemate():
                self._end_game("draw", "stalemate", msg["uci"])
            elif self.board.is_insufficient_material():
                self._end_game("draw", "insufficient_material", msg["uci"])
            elif self.board.is_fivefold_repetition():
                self._end_game("draw", "fivefold_repetition", msg["uci"])
            elif self.board.is_seventyfive_moves():
                self._end_game("draw", "seventyfive_moves", msg["uci"])
            else:
                self._broadcast(self._build_state_msg(msg["uci"]))

    def console_listener(self, srv: socket.socket) -> None:
        """thread to listen for exit"""
        while not self.game_over:
            cmd = input()
            if cmd.strip().lower() == "exit":
                print("[Server] closing on demand")
                self.game_over = True
                try:
                    #closing the port will terminate srv.accept()
                    srv.close() 
                except Exception:
                    pass
                break


    def _lan_broadcaster(self):
        """Thread sending UDP packets with server information into LAN"""
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        #local computer's ip
        local_ip = socket.gethostbyname(socket.gethostname())
        
        while not self.game_over:
            #count connected players
            players_count = sum(1 for c in self.clients if c is not None)
            
            #broadcast only when there are free slots to join
            if players_count < 2:
                msg = json.dumps({
                    "name": f"Pokój ({local_ip}:{self.port})",
                    "ip": local_ip,
                    "port": self.port,
                    "players": players_count
                }).encode('utf-8')
                
                try:
                    #brodcast to 8001
                    udp_sock.sendto(msg, ('<broadcast>', 8001))
                except Exception:
                    pass
            
            #broadcast every 1 scnd
            time.sleep(1)
            
        udp_sock.close()

    def run(self) -> None:
        """Starts the server, waits for two players, and starts the game."""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, 0))
        self.port = srv.getsockname()[1]
        srv.listen(2)
        print(f"[Server] Listening on {HOST}:{self.port} — waiting for two players")

        cmd_thread = threading.Thread(
            target=self.console_listener, 
            args=(srv,), 
            daemon=True
        )
        cmd_thread.start()

        udp_thread = threading.Thread(target=self._lan_broadcaster, daemon=True)
        udp_thread.start()

        try:
            for i in range(2):
                conn, addr = srv.accept()
                self.clients[i] = conn
                color = self.colors[i]
                print(f"[Server] Player {color} connected: {addr}")

                # Send information about the assigned color and initial FEN
                send_msg(conn, {
                    "type": "game_start",
                    "color": color,
                    "fen": self.board.fen(),
                })

            print("[Server] Both players connected — game started!")

            threads = []
            for i in range(2):
                t = threading.Thread(
                    target=self.handle_client,
                    args=(self.clients[i], i),
                    daemon=True,
                )
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        except OSError:
            #on pourpose when we type 'exit'
            if self.game_over:
                pass
            else:
                print("\nScocket problem")
        except KeyboardInterrupt:
            print("\n[Server] Stopped by Ctrl+C.")
        finally:
            self.game_over=True
            try:
                srv.close()
            except Exception:
                pass


if __name__ == "__main__":
    ChessServer().run()