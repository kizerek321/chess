import json

"""
protocol.py — Common module for communication protocol.

All messages are Python dictionaries serialized to JSON,
sent over TCP terminated with a newline character ('\\n').
"""

def send_msg(sock, data: dict) -> None:
    """Serializes a dictionary to JSON and sends it through a socket terminated with '\\n'."""
    raw = (json.dumps(data) + "\n").encode("utf-8")
    sock.sendall(raw)


def recv_msg(sock_file) -> dict | None:
    """
    Reads one line from a file-like socket object and deserializes JSON.

    Parameters:
        sock_file: file-like object returned by socket.makefile("r")

    Returns:
        Dictionary with the message or None when the connection is closed.
    """
    line = sock_file.readline()
    if not line:
        return None
    return json.loads(line.strip())
