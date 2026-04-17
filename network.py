import socket
import threading
import queue

from protocol import send_msg, recv_msg



class NetworkClient:
    """
    Class NetworkClient manages the TCP connection with the server.
    Incoming messages are received in a separate thread and
    placed in a queue that the Pygame loop polls through poll().
    """
    def __init__(self, host: str, port: int):
        """
        Connects to the server and starts a listening thread.

        Parameters:
            host: server IP address
            port: server TCP port
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self._file = self.sock.makefile("r", encoding="utf-8")
        self._message_queue: queue.Queue[dict] = queue.Queue()
        self._running = True

        recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        recv_thread.start()

    def _recv_loop(self) -> None:
        """Background thread: reads messages from the server and puts them in a queue."""
        while self._running:
            try:
                msg = recv_msg(self._file)
                if msg is None:
                    # Server closed the connection
                    self._message_queue.put({"type": "disconnected"})
                    break
                self._message_queue.put(msg)
            except Exception:
                if self._running:
                    self._message_queue.put({"type": "disconnected"})
                break

    def poll(self) -> dict | None:
        """
        Returns the next message from the server without blocking.
        Call once per frame in the Pygame loop.

        Returns:
            Message dictionary or None when no new messages.
        """
        try:
            return self._message_queue.get_nowait()
        except queue.Empty:
            return None

    def send_move(self, uci: str) -> None:
        """Sends a chess move in UCI notation (e.g. 'e2e4')."""
        send_msg(self.sock, {"type": "move", "uci": uci})

    def send_forfeit(self) -> None:
        """Sends information about the player's resignation."""
        send_msg(self.sock, {"type": "forfeit"})

    def close(self) -> None:
        """Closes the connection and stops the listening thread."""
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass
