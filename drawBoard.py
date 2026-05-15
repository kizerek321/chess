import pygame
import chess
import sys
from constants import *


def get_promotion_choice(color: chess.Color) -> int:
    pygame.draw.rect(screen, 'black', [300, 350, 400, 100])
    pygame.draw.rect(screen, 'gold', [300, 350, 400, 100], 3)
    
    images = white_images if color == chess.WHITE else black_images
    
    screen.blit(images[chess.QUEEN], (310, 360))
    screen.blit(images[chess.ROOK], (410, 360))
    screen.blit(images[chess.BISHOP], (510, 360))
    screen.blit(images[chess.KNIGHT], (610, 360))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if 350 <= y <= 450:
                    if 300 <= x < 400: return chess.QUEEN
                    elif 400 <= x < 500: return chess.ROOK
                    elif 500 <= x < 600: return chess.BISHOP
                    elif 600 <= x < 700: return chess.KNIGHT


def _sq_to_pixel(sq: int, flipped: bool) -> tuple[int, int]:
    """
    Process chess square number (0-63) to pixel coordinates (top-left corner).

    Parameters:
        sq:      square number according to python-chess (a1=0, h8=63)
        flipped: True when the board is rotated (black's perspective)

    Returns:
        (x, y) in pixels
    """
    file_idx = chess.square_file(sq)
    rank_idx = chess.square_rank(sq)

    if flipped:
        x = (7 - file_idx) * 100
        y = rank_idx * 100
    else:
        x = file_idx * 100
        y = (7 - rank_idx) * 100

    return x, y


def _pixel_to_sq(x_tile: int, y_tile: int, flipped: bool) -> int:
    """
    Process tile indices (column/row after dividing by 100) to square number.

    Parameters:
        x_tile:  board column (0-7)
        y_tile:  board row (0-7)
        flipped: True when the board is rotated

    Returns:
        Square number according to python-chess.
    """
    if flipped:
        file_idx = 7 - x_tile
        rank_idx = y_tile
    else:
        file_idx = x_tile
        rank_idx = 7 - y_tile

    return chess.square(file_idx, rank_idx)


def draw_board(state) -> None:
    """Draws the chessboard squares, status bar, and border."""
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 1:
            pygame.draw.rect(screen, 'Brown', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'Brown', [700 - (column * 200), row * 100, 100, 100])

    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)

    if state.board.turn == chess.WHITE:
        status_text = 'White: Select a Piece to Move!' if state.selection is None else 'White: Select a Destination!'
    else:
        status_text = 'Black: Select a Piece to Move!' if state.selection is None else 'Black: Select a Destination!'

    screen.blit(big_font.render(status_text, True, 'black'), (20, 820))

    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)

    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))


def draw_pieces(state) -> None:
    """Draws pieces on the board considering the player's perspective."""
    flipped = (state.my_color == chess.BLACK)

    for sq in chess.SQUARES:
        piece = state.board.piece_at(sq)
        if not piece:
            continue

        x_pos, y_pos = _sq_to_pixel(sq, flipped)

        image = white_images[piece.piece_type] if piece.color == chess.WHITE else black_images[piece.piece_type]

        if piece.piece_type == chess.PAWN:
            screen.blit(image, (x_pos + 8, y_pos + 18))
        else:
            screen.blit(image, (x_pos + 10, y_pos + 10))

        # Highlight selected piece
        if state.selection == sq:
            color = 'red' if state.board.turn == chess.WHITE else 'blue'
            pygame.draw.rect(screen, color, [x_pos + 1, y_pos + 1, 100, 100], 2)

    # Highlight last move (light yellow border)
    if state.last_move:
        try:
            last = chess.Move.from_uci(state.last_move)
            for highlight_sq in (last.from_square, last.to_square):
                hx, hy = _sq_to_pixel(highlight_sq, flipped)
                pygame.draw.rect(screen, (220, 200, 50), [hx + 1, hy + 1, 100, 100], 3)
        except ValueError:
            pass


def draw_valid(state, moves: list[int]) -> None:
    """Draws circles on legal destination squares."""
    flipped = (state.my_color == chess.BLACK)
    color = 'red' if state.board.turn == chess.WHITE else 'blue'
    for dest_sq in moves:
        x_pos, y_pos = _sq_to_pixel(dest_sq, flipped)
        pygame.draw.circle(screen, color, (x_pos + 50, y_pos + 50), 5)


def draw_captured(state) -> None:
    """Draws captured pieces on the side panel."""
    for i, piece_type in enumerate(state.captured_pieces_white):
        screen.blit(small_black_images[piece_type], (825, 5 + 50 * i))
    for i, piece_type in enumerate(state.captured_pieces_black):
        screen.blit(small_white_images[piece_type], (925, 5 + 50 * i))


def draw_check(state) -> None:
    """Draws a blinking border around the king in check."""
    if state.board.is_check():
        flipped = (state.my_color == chess.BLACK)
        king_sq = state.board.king(state.board.turn)
        if king_sq is not None and state.counter < 15:
            x_pos, y_pos = _sq_to_pixel(king_sq, flipped)
            color = 'dark red' if state.board.turn == chess.WHITE else 'dark blue'
            pygame.draw.rect(screen, color, [x_pos + 1, y_pos + 1, 100, 100], 5)


def draw_game_over(state) -> None:
    """Displays the game over panel."""
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    if state.winner == "Draw":
        screen.blit(font.render(f'{state.winner}!', True, 'white'), (210, 210))
    else:
        screen.blit(font.render(f'{state.winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render('Press ENTER to Restart!', True, 'white'), (210, 240))


def draw_waiting(state) -> None:
    """Displays the waiting screen for the second player."""
    pygame.draw.rect(screen, 'black', [150, 330, 500, 80])
    pygame.draw.rect(screen, 'gold', [150, 330, 500, 80], 3)
    color_text = "White" if state.my_color == chess.WHITE else "Black" if state.my_color == chess.BLACK else "?"
    screen.blit(font.render(f'You are {color_text}. Waiting for opponent...', True, 'white'), (160, 355))


def draw_pending(state) -> None:
    """Displays information about waiting for move confirmation."""
    pygame.draw.rect(screen, (30, 30, 30), [150, 755, 500, 40])
    screen.blit(medium_font.render('Waiting for server confirmation...', True, 'yellow'), (160, 763))

def draw_opponent_disconnected(state) -> None:
    """Displays information about the opponent being disconnected."""
    pygame.draw.rect(screen, (30, 30, 30), [150, 755, 560, 40])
    screen.blit(medium_font.render('Opponent disconnected. Waiting for opponent to reconnect...', True, 'yellow'), (160, 763))