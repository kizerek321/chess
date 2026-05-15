import socket
import threading
import chess
import json
import time

from protocol import send_msg, recv_msg

HOST = "0.0.0.0"

class ChessRoom:
    """Single game instance (room), running on its own port."""
    def __init__(self, room_name: str):
        self.room_name = room_name
        self.board = chess.Board()
        self.clients = [None, None]
        self.colors = ["white", "black"]
        self.lock = threading.Lock()
        
        self.captured_white = []
        self.captured_black = []
        self.game_over = False
        self.players_count = 0
        self.disconnect_timers = [None, None]
        self.client_ips = [None, None]

        # TCP socket for this room on a random port
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind((HOST, 0))
        self.port = self.srv.getsockname()[1]
        self.srv.listen(2)

        # Starting a thread to accept 2 players for this room
        threading.Thread(target=self._accept_players, daemon=True).start()

    def _accept_players(self):
        try:
            while not self.game_over:
                conn, addr = self.srv.accept()
                
                with self.lock:
                    if self.clients[0] is None:
                        slot = 0
                    elif self.clients[1] is None:
                        slot = 1
                    else:
                        conn.close()
                        continue
                        
                    ip = addr[0]
                    # Verify IP to restrict reconnect to the original player
                    # does not work on single machine but for local network will work
                    if self.client_ips[slot] is not None and self.client_ips[slot] != ip:
                        print(f"[{self.room_name}] Rejected {ip} (slot {slot} reserved for {self.client_ips[slot]})")
                        conn.close()
                        continue
                        
                    self.clients[slot] = conn
                    self.client_ips[slot] = ip
                    self.players_count += 1
                    color = self.colors[slot]
                    print(f"[{self.room_name}] Player {color} joined/rejoined: {addr}")

                    if self.disconnect_timers[slot]:
                        self.disconnect_timers[slot].cancel()
                        self.disconnect_timers[slot] = None
                        self._send_to(1 - slot, {"type": "opponent_reconnected"})

                    send_msg(conn, {
                        "type": "game_start",
                        "color": color,
                        "fen": self.board.fen(),
                    })

                    threading.Thread(target=self.handle_client, args=(conn, slot), daemon=True).start()
        except OSError:
            pass # Room was closed early

    def _broadcast(self, msg: dict) -> None:
        for conn in self.clients:
            if conn:
                try: send_msg(conn, msg)
                except Exception: pass

    def _send_to(self, player_idx: int, msg: dict) -> None:
        conn = self.clients[player_idx]
        if conn:
            try: send_msg(conn, msg)
            except Exception: pass

    def _build_state_msg(self, last_move_uci: str | None) -> dict:
        return {
            "type": "move_ok",
            "fen": self.board.fen(),
            "last_move": last_move_uci,
            "captured_white": self.captured_white[:],
            "captured_black": self.captured_black[:],
        }

    def _end_game(self, result: str, reason: str, last_move_uci: str | None) -> None:
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
        color = self.colors[player_idx]
        client_chess_color = chess.WHITE if color == "white" else chess.BLACK
        sock_file = conn.makefile("r", encoding="utf-8")

        try:
            while True:
                msg = recv_msg(sock_file)
                if msg is None:
                    print(f"[{self.room_name}] Player {color} disconnected.")
                    break

                if msg["type"] == "move":
                    self._handle_move(msg, player_idx, client_chess_color, color)

                elif msg["type"] == "forfeit":
                    with self.lock:
                        if not self.game_over:
                            winner = "black" if color == "white" else "white"
                            print(f"[{self.room_name}] Player {color} forfeited.")
                            self._end_game(f"{winner}_wins", "forfeit", None)
        except Exception as e:
            pass
        finally:
            conn.close()
            with self.lock:
                self.clients[player_idx] = None
                if not self.game_over:
                    self.players_count -= 1
                    self._send_to(1 - player_idx, {"type": "opponent_disconnected"})
                    timer = threading.Timer(30.0, self._end_game, args=("disconnected", "Opponent disconnected", None))
                    self.disconnect_timers[player_idx] = timer
                    timer.start()


    def _handle_move(self, msg: dict, player_idx: int, client_chess_color: chess.Color, color: str) -> None:
        with self.lock:
            if self.game_over: return

            if self.board.turn != client_chess_color:
                self._send_to(player_idx, {"type": "move_rejected", "reason": "Not your turn"})
                return

            try: move = chess.Move.from_uci(msg["uci"])
            except (ValueError, KeyError):
                self._send_to(player_idx, {"type": "move_rejected", "reason": "Invalid UCI"})
                return

            if move not in self.board.legal_moves:
                self._send_to(player_idx, {"type": "move_rejected", "reason": "Illegal move"})
                return

            if self.board.is_en_passant(move):
                captured_type = chess.PAWN
            else:
                target = self.board.piece_at(move.to_square)
                captured_type = target.piece_type if target else None

            if captured_type:
                if self.board.turn == chess.WHITE: self.captured_white.append(captured_type)
                else: self.captured_black.append(captured_type)

            self.board.push(move)
            print(f"[{self.room_name}] Ruch {color}: {msg['uci']}")

            if self.board.is_checkmate():
                winner = "white" if self.board.turn == chess.BLACK else "black"
                self._end_game(f"{winner}_wins", "checkmate", msg["uci"])
            elif self.board.is_stalemate(): self._end_game("draw", "stalemate", msg["uci"])
            elif self.board.is_insufficient_material(): self._end_game("draw", "insufficient_material", msg["uci"])
            elif self.board.is_fivefold_repetition(): self._end_game("draw", "fivefold_repetition", msg["uci"])
            elif self.board.is_seventyfive_moves(): self._end_game("draw", "seventyfive_moves", msg["uci"])
            else:
                self._broadcast(self._build_state_msg(msg["uci"]))

    def close(self):
        """Zamyka pokój i zwalnia port."""
        self.game_over = True
        try:
            self.srv.close()
        except Exception:
            pass