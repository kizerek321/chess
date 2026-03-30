import pygame
import chess
from drawBoard import *
from constants import *
from game_state import GameState


state = GameState()

run = True
while run:
    timer.tick(fps)
    if state.counter < 30:
        state.counter += 1
    else:
        state.counter = 0
        
    screen.fill('azure')
    draw_board(state)
    draw_pieces(state)
    draw_captured(state)
    draw_check(state)
    
    if state.selection is not None:
        draw_valid(state, state.valid_moves)

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        # Handling left mouse button clicks when the game is not over
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not state.game_over:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            
            # Check if the player clicked on forfeit squares
            if x_coord in (8, 9) and y_coord == 8:
                state.winner = 'Black' if state.board.turn == chess.WHITE else 'White'
                state.game_over = True
            elif x_coord < 8 and y_coord < 8:
                clicked_sq = chess.square(x_coord, 7 - y_coord)
                
                # Check game over conditions before moving string
                if state.board.is_checkmate():
                    state.winner = 'Black' if state.board.turn == chess.WHITE else 'White'
                    state.game_over = True
                elif state.board.is_game_over():
                    state.winner = 'Draw'
                    state.game_over = True
                
                if not state.game_over:
                    # Handling piece selection and moving
                    if state.selection is None:
                        # Select a piece if it belongs to current player
                        piece = state.board.piece_at(clicked_sq)
                        if piece and piece.color == state.board.turn:
                            state.selection = clicked_sq
                            state.valid_moves = [move.to_square for move in state.board.legal_moves if move.from_square == clicked_sq]
                    else:
                        # Destination is clicked
                        piece = state.board.piece_at(clicked_sq)
                        if piece and piece.color == state.board.turn:
                            state.selection = clicked_sq
                            state.valid_moves = [move.to_square for move in state.board.legal_moves if move.from_square == clicked_sq]
                        elif clicked_sq in state.valid_moves:
                            # Find the actual move
                            move_to_make = None
                            for move in state.board.legal_moves:
                                if move.from_square == state.selection and move.to_square == clicked_sq:
                                    # Handle promotion (auto-promote to Queen) - TODO: Add promotion GUI
                                    if move.promotion:
                                        if move.promotion == chess.QUEEN:
                                            move_to_make = move
                                            break
                                    else:
                                        move_to_make = move
                                        break
                            
                            if move_to_make:
                                # Track captured pieces before pushing move
                                target_piece = state.board.piece_at(clicked_sq)
                                if state.board.is_en_passant(move_to_make):
                                    captured_type = chess.PAWN
                                elif target_piece:
                                    captured_type = target_piece.piece_type
                                else:
                                    captured_type = None

                                if captured_type:
                                    if state.board.turn == chess.WHITE:
                                        state.captured_pieces_white.append(captured_type)
                                    else:
                                        state.captured_pieces_black.append(captured_type)
                                        
                                state.board.push(move_to_make)
                                state.selection = None
                                state.valid_moves = []
                                
                                # check after move if game over
                                if state.board.is_checkmate():
                                    state.winner = 'White' if state.board.turn == chess.BLACK else 'Black'
                                    state.game_over = True
                                elif state.board.is_game_over():
                                    state.winner = 'Draw'
                                    state.game_over = True
                        else:
                            # Invalid square click, deselect
                            state.selection = None
                            state.valid_moves = []

        # Handling key press events when the game is over
        if event.type == pygame.KEYDOWN and state.game_over:
            if event.key == pygame.K_RETURN:
                state.reset_state()

    # Checking for a winner and displaying game over message
    if state.game_over:
        draw_game_over(state)

    # Update display
    pygame.display.flip()

pygame.quit()