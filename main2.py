import pygame

# Configuration
WIDTH, HEIGHT = 600, 600
CHESS_SIZE = 8
SQ_SIZE = WIDTH // CHESS_SIZE
WHITE = (235, 235, 208)
GREEN = (119, 149, 86)
HIGHLIGHT = (186, 202, 68)

class ChessGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.board = self.create_board()
        self.selected_sq = None
        self.turn = 'w'

    def create_board(self):
        # r, n, b, q, k, b, n, r (lowercase black, uppercase white)
        return [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p"] * 8,
            [""] * 8, [ ""] * 8, [ ""] * 8, [ ""] * 8,
            ["P"] * 8,
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

    def draw_board(self):
        for r in range(CHESS_SIZE):
            for c in range(CHESS_SIZE):
                color = WHITE if (r + c) % 2 == 0 else GREEN
                if self.selected_sq == (r, c):
                    color = HIGHLIGHT
                pygame.draw.rect(self.screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
                # Render text labels since we don't have png files here
                piece = self.board[r][c]
                if piece:
                    font = pygame.font.SysFont("Arial", 32, bold=True)
                    txt_color = (0, 0, 0) if piece.islower() else (255, 255, 255)
                    text = font.render(piece.upper(), True, txt_color)
                    self.screen.blit(text, (c*SQ_SIZE + 20, r*SQ_SIZE + 15))

    def move_piece(self, start, end):
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]

        # Simple logic: check if it's the right turn and not moving to own piece
        if (piece.isupper() and self.turn == 'w') or (piece.islower() and self.turn == 'b'):
            target = self.board[r2][c2]
            if target == "" or (target.isupper() != piece.isupper()):
                self.board[r2][c2] = piece
                self.board[r1][c1] = ""
                self.turn = 'b' if self.turn == 'w' else 'w'

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    location = pygame.mouse.get_pos()
                    col, row = location[0] // SQ_SIZE, location[1] // SQ_SIZE
                    
                    if self.selected_sq:
                        if self.selected_sq != (row, col):
                            self.move_piece(self.selected_sq, (row, col))
                        self.selected_sq = None
                    else:
                        if self.board[row][col] != "":
                            self.selected_sq = (row, col)

            self.draw_board()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    ChessGame().run()