import pygame
from constants import *

# function to check all pieces valid options on board
def check_options(pieces, locations, turn, state):
    moves_list = []
    all_moves_list = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn, state)
        elif piece == 'rook':
            moves_list = check_rook(location, turn, state)
        elif piece == 'knight':
            moves_list = check_knight(location, turn, state)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn, state)
        elif piece == 'queen':
            moves_list = check_queen(location, turn, state)
        elif piece == 'king':
            moves_list = check_king(location, turn, state)
        all_moves_list.append(moves_list)
    return all_moves_list


# check king valid moves
def check_king(position, color, state):
    moves_list = []
    if color == 'white':
        enemies_list = state.black_locations
        friends_list = state.white_locations
    else:
        friends_list = state.black_locations
        enemies_list = state.white_locations
    # 8 squares to check for kings, they can go one square any direction
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0),
               (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list

# check queen valid moves
def check_queen(position, color, state):
    moves_list = check_bishop(position, color, state)
    second_list = check_rook(position, color, state)
    for i in range(len(second_list)):
        moves_list.append(second_list[i])
    return moves_list


# check bishop moves
def check_bishop(position, color, state):
    moves_list = []
    if color == 'white':
        enemies_list = state.black_locations
        friends_list = state.white_locations
    else:
        friends_list = state.black_locations
        enemies_list = state.white_locations
    for i in range(4):  # up-right, up-left, down-right, down-left
        path = True
        chain = 1
        if i == 0:
            x = 1
            y = -1
        elif i == 1:
            x = -1
            y = -1
        elif i == 2:
            x = 1
            y = 1
        else:
            x = -1
            y = 1
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append(
                    (position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# check rook moves
def check_rook(position, color, state):
    moves_list = []
    if color == 'white':
        enemies_list = state.black_locations
        friends_list = state.white_locations
    else:
        friends_list = state.black_locations
        enemies_list = state.white_locations
    for i in range(4):  # down, up, right, left
        path = True
        chain = 1
        if i == 0:
            x = 0
            y = 1
        elif i == 1:
            x = 0
            y = -1
        elif i == 2:
            x = 1
            y = 0
        else:
            x = -1
            y = 0
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append(
                    (position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# check valid pawn moves
def check_pawn(position, color, state):
    moves_list = []
    if color == 'white':
        if (position[0], position[1] + 1) not in state.white_locations and \
                (position[0], position[1] + 1) not in state.black_locations and position[1] < 7:
            moves_list.append((position[0], position[1] + 1))
        if (position[0], position[1] + 2) not in state.white_locations and \
                (position[0], position[1] + 2) not in state.black_locations and position[1] == 1:
            moves_list.append((position[0], position[1] + 2))
        if (position[0] + 1, position[1] + 1) in state.black_locations:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) in state.black_locations:
            moves_list.append((position[0] - 1, position[1] + 1))
    else:
        if (position[0], position[1] - 1) not in state.white_locations and \
                (position[0], position[1] - 1) not in state.black_locations and position[1] > 0:
            moves_list.append((position[0], position[1] - 1))
        if (position[0], position[1] - 2) not in state.white_locations and \
                (position[0], position[1] - 2) not in state.black_locations and position[1] == 6:
            moves_list.append((position[0], position[1] - 2))
        if (position[0] + 1, position[1] - 1) in state.white_locations:
            moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) in state.white_locations:
            moves_list.append((position[0] - 1, position[1] - 1))
    return moves_list


# check valid knight moves
def check_knight(position, color, state):
    moves_list = []
    if color == 'white':
        enemies_list = state.black_locations
        friends_list = state.white_locations
    else:
        friends_list = state.black_locations
        enemies_list = state.white_locations
    # 8 squares to check for knights, they can go two squares in one direction and one in another
    targets = [(1, 2), (1, -2), (2, 1), (2, -1),
               (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


# check for valid moves for just selected piece
def check_valid_moves(state):
    if state.turn_step < 2:
        options_list = state.white_options
    else:
        options_list = state.black_options
    if state.selection < len(options_list):
        valid_options = options_list[state.selection]
    else:
        valid_options = []
    return valid_options