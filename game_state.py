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

    def reset_state(self):
        self.__init__()
