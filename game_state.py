import chess


class GameState:
    def __init__(self):
        self.counter = 0
        self.winner = ''
        self.game_over = False

        # Core game logic using python-chess
        self.board = chess.Board()

        # Pygame board visual selections
        self.selection = None
        self.valid_moves = []

        # Pieces captured by each side.
        # We'll store chess.PieceType integers (1-6)
        self.captured_pieces_white = []
        self.captured_pieces_black = []

        # Network fields for multiplayer mode

        # Color assigned by the server: chess.WHITE or chess.BLACK
        self.my_color: chess.Color | None = None

        # True when a move has been sent to the server and we are waiting for move_ok/move_rejected
        self.pending_move: bool = False

        # True when connected to the server and received game_start
        self.connected: bool = False

        # UCI notation of the last move for highlighting (e.g. "e2e4")
        self.last_move: str | None = None

    def reset_state(self):
        self.__init__()
