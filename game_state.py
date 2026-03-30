class GameState:
    def __init__(self):
        self.counter = 0
        self.winner = ''
        self.game_over = False
        self.white_ep = (100, 100)
        self.black_ep = (100, 100)
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100
        self.check = False
        self.castling_moves = []
        
        self.white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                             'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
        self.white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
        self.black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                             'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
        self.black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]

        self.captured_pieces_white = []
        self.captured_pieces_black = []

        self.turn_step = 0
        self.selection = 100
        self.valid_moves = []

        self.white_moved = [False, False, False, False, False, False, False, False,
                            False, False, False, False, False, False, False, False]
        self.black_moved = [False, False, False, False, False, False, False, False,
                            False, False, False, False, False, False, False, False]

        self.white_options = []
        self.black_options = []

    def reset_state(self):
        self.__init__()
