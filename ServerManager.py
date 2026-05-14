import socket
import threading
import chess
import json
import time

from protocol import send_msg, recv_msg
from chessRoom import ChessRoom


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
            # Ensure there is always at least one available room
            available_rooms = sum(1 for room in list(self.rooms) if room.players_count < 2 and not room.game_over)
            if available_rooms == 0:
                self._create_room()

            # Broadcast each active room that needs players
            for room in list(self.rooms):
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
            
            # Clean up closed rooms from the list to prevent memory leak
            self.rooms = [r for r in self.rooms if not r.game_over]
            
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