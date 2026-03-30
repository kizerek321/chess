import pygame
from checkers import *
from drawBoard import *
from constants import *
from game_state import GameState


state = GameState()
state.black_options = check_options(state.black_pieces, state.black_locations, 'black', state)
state.white_options = check_options(state.white_pieces, state.white_locations, 'white', state)

run = True
while run:
    timer.tick(fps)
    if state.counter < 30:
        state.counter += 1
    else:
        state.counter = 0
        
    screen.fill('dark gray')
    draw_board(state)
    draw_pieces(state)
    draw_captured(state)
    draw_check(state)
    
    if state.selection != 100:
        state.valid_moves = check_valid_moves(state)
        draw_valid(state, state.valid_moves)

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Handling left mouse button clicks when the game is not over
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not state.game_over:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            click_coords = (x_coord, y_coord)
            # Handling player input during the first two turns
            if state.turn_step <= 1:
                # Check if the player clicked on forfeit squares
                if click_coords == (8, 8) or click_coords == (9, 8):
                    state.winner = 'black'
                # Check if the clicked coordinates belong to white pieces
                if click_coords in state.white_locations:
                    state.selection = state.white_locations.index(click_coords)
                    if state.turn_step == 0:
                        state.turn_step = 1
                # Check if the clicked coordinates are valid moves for the selected white piece
                if click_coords in state.valid_moves and state.selection != 100:
                    state.white_locations[state.selection] = click_coords
                    # Check for capturing black pieces
                    if click_coords in state.black_locations:
                        black_piece = state.black_locations.index(click_coords)
                        state.captured_pieces_white.append(state.black_pieces[black_piece])
                        if state.black_pieces[black_piece] == 'king':
                            state.winner = 'white'
                        state.black_pieces.pop(black_piece)
                        state.black_locations.pop(black_piece)
                    # Update move options for both black and white
                    state.black_options = check_options(
                        state.black_pieces, state.black_locations, 'black', state)
                    state.white_options = check_options(
                        state.white_pieces, state.white_locations, 'white', state)
                    state.turn_step = 2
                    state.selection = 100
                    state.valid_moves = []
            # Handling player input during the last two turns
            if state.turn_step > 1:
                # Check if the player clicked on forfeit squares
                if click_coords == (8, 8) or click_coords == (9, 8):
                    state.winner = 'white'
                # Check if the clicked coordinates belong to black pieces
                if click_coords in state.black_locations:
                    state.selection = state.black_locations.index(click_coords)
                    if state.turn_step == 2:
                        state.turn_step = 3
                # Check if the clicked coordinates are valid moves for the selected black piece
                if click_coords in state.valid_moves and state.selection != 100:
                    state.black_locations[state.selection] = click_coords
                    # Check for capturing white pieces
                    if click_coords in state.white_locations:
                        white_piece = state.white_locations.index(click_coords)
                        state.captured_pieces_black.append(state.white_pieces[white_piece])
                        if state.white_pieces[white_piece] == 'king':
                            state.winner = 'black'
                        state.white_pieces.pop(white_piece)
                        state.white_locations.pop(white_piece)
                    # Update move options for both black and white
                    state.black_options = check_options(
                        state.black_pieces, state.black_locations, 'black', state)
                    state.white_options = check_options(
                        state.white_pieces, state.white_locations, 'white', state)
                    state.turn_step = 0
                    state.selection = 100
                    state.valid_moves = []

        # Handling key press events when the game is over
        if event.type == pygame.KEYDOWN and state.game_over:
            # Check if the pressed key is the "Enter" key
            if event.key == pygame.K_RETURN:
                # Resetting the game state when the "Enter" key is pressed
                state.reset_state()
                state.black_options = check_options(state.black_pieces, state.black_locations, 'black', state)
                state.white_options = check_options(state.white_pieces, state.white_locations, 'white', state)

    # Checking for a winner and displaying game over message
    if state.winner != '':
        state.game_over = True
        draw_game_over(state)

    # Update display
    pygame.display.flip()

pygame.quit()