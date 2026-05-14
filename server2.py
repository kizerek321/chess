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
            for i in range(2):
                conn, addr = self.srv.accept()
                self.clients[i] = conn
                self.players_count += 1
                color = self.colors[i]
                print(f"[{self.room_name}] Player {color} joined: {addr}")

                send_msg(conn, {
                    "type": "game_start",
                    "color": color,
                    "fen": self.board.fen(),
                })

            print(f"[{self.room_name}] Both players have joined — game start!")

            # Start listening for moves from players
            for i in range(2):
                threading.Thread(target=self.handle_client, args=(self.clients[i], i), daemon=True).start()
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
            while not self.game_over:
                msg = recv_msg(sock_file)
                if msg is None:
                    print(f"[{self.room_name}] Gracz {color} rozłączył się.")
                    break

                if msg["type"] == "move":
                    self._handle_move(msg, player_idx, client_chess_color, color)

                elif msg["type"] == "forfeit":
                    with self.lock:
                        winner = "black" if color == "white" else "white"
                        print(f"[{self.room_name}] Gracz {color} poddał się.")
                        self._end_game(f"{winner}_wins", "forfeit", None)
        except Exception as e:
            pass
        finally:
            conn.close()
            # If player disconnects, close the room to avoid hanging the other player
            # change to measure 30 seconds of wainting for rejoing of player
            self.game_over = True 

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

def get_local_ip():
    # Create a temporary socket to check which interface we are using to connect to the internet
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"


class ServerManager:
    """Main manager for managing rooms and broadcasting in LAN."""
    def __init__(self):
        self.rooms: list[ChessRoom] = []
        self.running = True
        self.room_counter = 1

    def _lan_broadcaster(self):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #local_ip = socket.gethostbyname(socket.gethostname())
        local_ip = get_local_ip()

        while self.running:
            # Broadcast each active room that needs players
            for room in self.rooms:
                if room.players_count < 2 and not room.game_over:
                    msg = json.dumps({
                        "name": room.room_name,
                        "ip": local_ip,
                        "port": room.port,
                        "players": room.players_count
                    }).encode('utf-8')
                    try:
                        udp_sock.sendto(msg, ('<broadcast>', 8001))
                    except Exception:
                        pass
            time.sleep(1)
        udp_sock.close()

    def _create_room(self):
        name = f"Room {self.room_counter}"
        new_room = ChessRoom(name)
        self.rooms.append(new_room)
        print(f"[Manager] Opened {name} on port {new_room.port}")
        self.room_counter += 1

    def run(self):
        print(f"--- CHESS SERVER LAUNCHED ---")
        print("Commands: 'add room' (new room), 'exit' (shutting down server)\n")

        # Start LAN broadcasting thread
        threading.Thread(target=self._lan_broadcaster, daemon=True).start()
        
        # Open first room for start
        self._create_room()

        # Main console loop
        while self.running:
            cmd = input().strip().lower()
            if cmd == "exit":
                print("[Manager] Shutting down all rooms...")
                self.running = False
                for room in self.rooms:
                    room.close()
                break
            elif cmd == "add room":
                self._create_room()
            else:
                print("[Menedżer] Nieznana komenda.")

if __name__ == "__main__":
    ServerManager().run()