import pygame
import chess
from constants import *

def draw_board(state):
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [
                             600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [
                             700 - (column * 200), row * 100, 100, 100])
    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
    
    if state.board.turn == chess.WHITE:
        if state.selection is None:
            status_text = 'White: Select a Piece to Move!'
        else:
            status_text = 'White: Select a Destination!'
    else:
        if state.selection is None:
            status_text = 'Black: Select a Piece to Move!'
        else:
            status_text = 'Black: Select a Destination!'
            
    screen.blit(big_font.render(status_text, True, 'black'), (20, 820))
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))


# draw pieces onto board
def draw_pieces(state):
    for sq in chess.SQUARES:
        piece = state.board.piece_at(sq)
        if piece:
            file_idx = chess.square_file(sq)
            rank_idx = 7 - chess.square_rank(sq)
            
            x_pos = file_idx * 100
            y_pos = rank_idx * 100
            
            if piece.color == chess.WHITE:
                image = white_images[piece.piece_type]
            else:
                image = black_images[piece.piece_type]
                
            if piece.piece_type == chess.PAWN:
                screen.blit(image, (x_pos + 8, y_pos + 18))
            else:
                screen.blit(image, (x_pos + 10, y_pos + 10))
                
            if state.selection == sq:
                color = 'red' if state.board.turn == chess.WHITE else 'blue'
                pygame.draw.rect(screen, color, [x_pos + 1, y_pos + 1, 100, 100], 2)


def draw_valid(state, moves):
    color = 'red' if state.board.turn == chess.WHITE else 'blue'
    for dest_sq in moves:
        file_idx = chess.square_file(dest_sq)
        rank_idx = 7 - chess.square_rank(dest_sq)
        pygame.draw.circle(
            screen, color, (file_idx * 100 + 50, rank_idx * 100 + 50), 5)


# draw captured pieces on side of screen
def draw_captured(state):
    for i in range(len(state.captured_pieces_white)):
        piece_type = state.captured_pieces_white[i]
        screen.blit(small_black_images[piece_type], (825, 5 + 50 * i))
    for i in range(len(state.captured_pieces_black)):
        piece_type = state.captured_pieces_black[i]
        screen.blit(small_white_images[piece_type], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check(state):
    if state.board.is_check():
        king_sq = state.board.king(state.board.turn)
        if king_sq is not None and state.counter < 15:
            file_idx = chess.square_file(king_sq)
            rank_idx = 7 - chess.square_rank(king_sq)
            color = 'dark red' if state.board.turn == chess.WHITE else 'dark blue'
            pygame.draw.rect(screen, color, [file_idx * 100 + 1, rank_idx * 100 + 1, 100, 100], 5)

def draw_game_over(state):
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(
        f'{state.winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!',
                            True, 'white'), (210, 240))