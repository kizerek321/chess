import pygame
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
    status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                   'Black: Select a Piece to Move!', 'Black: Select a Destination!']
    screen.blit(big_font.render(
        status_text[state.turn_step], True, 'black'), (20, 820))
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))


# draw pieces onto board
def draw_pieces(state):
    for i in range(len(state.white_pieces)):
        index = piece_list.index(state.white_pieces[i])
        if state.white_pieces[i] == 'pawn':
            screen.blit(
                white_images[index], (state.white_locations[i][0] * 100 + 8, state.white_locations[i][1] * 100 + 18))
        else:
            screen.blit(white_images[index], (state.white_locations[i]
                                              [0] * 100 + 10, state.white_locations[i][1] * 100 + 10))
        if state.turn_step < 2:
            if state.selection == i:
                pygame.draw.rect(screen, 'red', [state.white_locations[i][0] * 100 + 1, state.white_locations[i][1] * 100 + 1,
                                                 100, 100], 2)

    for i in range(len(state.black_pieces)):
        index = piece_list.index(state.black_pieces[i])
        if state.black_pieces[i] == 'pawn':
            screen.blit(
                black_images[index], (state.black_locations[i][0] * 100 + 8, state.black_locations[i][1] * 100 + 18))
        else:
            screen.blit(black_images[index], (state.black_locations[i]
                                              [0] * 100 + 10, state.black_locations[i][1] * 100 + 10))
        if state.turn_step >= 2:
            if state.selection == i:
                pygame.draw.rect(screen, 'blue', [
                                state.black_locations[i][0] * 100 + 1, state.black_locations[i][1] * 100 + 1, 100, 100], 2)

def draw_valid(state, moves):
    if state.turn_step < 2:
        color = 'red'
    else:
        color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(
            screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)


# draw captured pieces on side of screen
def draw_captured(state):
    for i in range(len(state.captured_pieces_white)):
        captured_piece = state.captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(state.captured_pieces_black)):
        captured_piece = state.captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check(state):
    if state.turn_step < 2:
        if 'king' in state.white_pieces:
            king_index = state.white_pieces.index('king')
            king_location = state.white_locations[king_index]
            for i in range(len(state.black_options)):
                if king_location in state.black_options[i]:
                    if state.counter < 15:
                        pygame.draw.rect(screen, 'dark red', [state.white_locations[king_index][0] * 100 + 1,
                                                              state.white_locations[king_index][1] * 100 + 1, 100, 100], 5)
    else:
        if 'king' in state.black_pieces:
            king_index = state.black_pieces.index('king')
            king_location = state.black_locations[king_index]
            for i in range(len(state.white_options)):
                if king_location in state.white_options[i]:
                    if state.counter < 15:
                        pygame.draw.rect(screen, 'dark blue', [state.black_locations[king_index][0] * 100 + 1,
                                                               state.black_locations[king_index][1] * 100 + 1, 100, 100], 5)


def draw_game_over(state):
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(
        f'{state.winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!',
                            True, 'white'), (210, 240))