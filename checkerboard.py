import terminal
import math
from functools import lru_cache

BOARD_SIZE = 8
CELLS = BOARD_SIZE * BOARD_SIZE
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SELECTED = set()
TARGETS = set()

PAWN_VALUE = 1
KING_VALUE = 4

EMPTY = 0
WHITE_PAWN = 1
WHITE_KING = 2
BLACK_PAWN = 3
BLACK_KING = 4
WHITE = 5
BLACK = 6

PIECES_TO_STR = (' ', '●', '◉', '●', '◉')

def set_target(index):
    """Sets one of the possible highlighted target squares"""
    TARGETS.add(index)

def clear_target():
    """Removes any targeting from the board"""
    global TARGETS
    TARGETS = set()

def set_selected(index):
    """Adds the provided index to the selected list"""  
    SELECTED.add(index)

def clear_selected():
    """Clears all selections"""
    global SELECTED
    SELECTED = set()

def transfer_turn(board):
    """Sets the turn to the opposite player"""
    return -board

def get_current_player(board, as_str=False):
    """Returns the current player"""
    if not as_str: return BLACK if board < 0 else WHITE
    return 'black' if board < 0 else 'white'

@lru_cache(maxsize=1)
def get_init():
    """Gets a board in the normal starting positions"""
    board = 0
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            is_white = (x + y) % 2 != 0
            is_top = y < 3
            is_bottom = y >= BOARD_SIZE - 3
            index = coord_to_index(x, y)

            if is_white and (is_bottom or is_top):
                piece = WHITE_KING if is_bottom else BLACK_PAWN
                board = set_piece(board, index, piece)
    return board

def move_piece(board, source_index, dest_index):
    """Moves the piece from the source index to the destination index"""
    piece = get_piece(board, source_index)
    board = set_piece(board, dest_index, piece)
    board = set_piece(board, source_index, EMPTY)

    source_x, source_y = index_to_coord(source_index)
    dest_x, dest_y = index_to_coord(dest_index)
    diff = abs(source_x - dest_x)
    if diff == 1: return board

    dir_x = 1 if dest_x > source_x else -1
    dir_y = 1 if dest_y > source_y else -1

    for offset in range(1, diff):
        off_x = dir_x * offset
        off_y = dir_y * offset
        off_index = coord_to_index(source_x + off_x, source_y + off_y)
        board = set_piece(board, off_index, EMPTY)

    return board

def get_piece(board, index):
    """Returns the nth piece of the provided board"""
    board = board if board >= 0 else -board
    return (board % 10 ** (index + 1)) // 10 ** index

def set_piece(board, index, val):
    """Sets the nth piece of the provided board"""
    negative = board < 0
    board = board if board >= 0 else -board
    factor = 10 ** index
    chopped = board // factor
    leftover = board % factor

    old_piece = chopped % 10
    chopped -= old_piece
    chopped += val

    modified_board = (chopped * factor) + leftover
    if negative: modified_board *= -1
    return modified_board

def get_possible_jumps(board):
    """Returns all the jumps that are possible on this board for the current player"""
    possible_jumps = []
    for index in range(CELLS):
        possible_jumps += [(index, jump) for jump in get_possible_jumps_from(board, index)]
    return possible_jumps

def get_possible_jumps_from(board, index):
    """Returns all the possible jumps from the provided index on the board for the current player"""
    piece = get_piece(board, index)
    if piece == EMPTY: return []
    player = get_current_player(board)

    if player == BLACK and piece < BLACK_PAWN: return []
    elif player == WHITE and piece >= BLACK_PAWN: return []

    is_pawn = piece % 2 != 0
    is_black = piece >= BLACK_PAWN
    x, y = index_to_coord(index)
    direction = 1 if is_black else -1
    length = 2 if is_pawn else BOARD_SIZE

    legals = []
    for dist in range(2, length + 1):
        forward = y + (direction * dist)
        backward = y - (direction * dist)
        left = x - dist
        right = x + dist
        legals += [(left, forward), (right, forward)]
        if not is_pawn: legals += [(left, backward), (right, backward)]

    jumps = []
    for x, y in legals:
        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE: continue
        jump_index = coord_to_index(x, y)
        piece = get_piece(board, jump_index)
        if piece == EMPTY and _jumped_over_single_piece(board, index, jump_index): 
            jumps.append(jump_index)

    return jumps

def _jumped_over_single_piece(board, source, dest):
    """Returns if we have jumped over a single piece or if this was just a move"""
    source_x, source_y = index_to_coord(source)
    player = get_current_player(board)
    dest_x, dest_y = index_to_coord(dest)
    diff = abs(dest_x - source_x)
    dir_x = 1 if dest_x > source_x else -1
    dir_y = 1 if dest_y > source_y else -1
    
    jumped = 0
    for offset in range(1, diff):
        inbetween_x = source_x + offset * dir_x
        inbetween_y = source_y + offset * dir_y
        inbetween_index = coord_to_index(inbetween_x, inbetween_y)
        piece = get_piece(board, inbetween_index)

        if piece == EMPTY: 
            continue        
        if player == BLACK and piece < BLACK_PAWN: jumped += 1
        if player == WHITE and piece >= BLACK_PAWN: jumped += 1

        if jumped >= 2: break

    return jumped == 1

def get_possible_moves(board):
    """Returns all the legal moves for each of the pieces on the board of the current player"""
    jumps = get_possible_jumps(board)
    if len(jumps) > 0: return jumps

    possible_moves = []
    for index in range(CELLS):
        possible_moves += [(index, move) for move in get_possible_moves_from(board, index)]
    return possible_moves

def get_possible_moves_from(board, index):
    """Returns all the possible moves from the provided starting position on the current board state"""
    jumps = get_possible_jumps_from(board, index)
    if len(jumps) > 0: return jumps

    piece = get_piece(board, index)
    if piece == EMPTY: return []
    player = get_current_player(board)

    if player == BLACK and piece < BLACK_PAWN: return []
    elif player == WHITE and piece >= BLACK_PAWN: return []
    
    is_pawn = piece % 2 != 0
    is_black = piece >= BLACK_PAWN
    x, y = index_to_coord(index)
    direction = 1 if is_black else -1
    length = 1 if is_pawn else BOARD_SIZE

    legals = []
    for dist in range(length + 1):
        forward = y + (direction * dist)
        backward = y - (direction * dist)
        left = x - dist
        right = x + dist
        legals += [(left, forward), (right, forward)]
        if not is_pawn: legals += [(left, backward), (right, backward)]

    moves = []
    for x, y in legals:
        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE: continue
        move_index = coord_to_index(x, y)
        piece = get_piece(board, move_index)
        if piece == EMPTY: moves.append(move_index)

    return moves

def get_score(board):
    """Returns a tuple holding the score for white and black"""
    black_score = 0
    white_score = 0
    for index in range(CELLS):
        piece = get_piece(board, index)
        if piece == EMPTY: continue
        elif piece >= BLACK_PAWN: 
            black_score += PAWN_VALUE + (piece - BLACK_PAWN) * KING_VALUE
        else:
            white_score += PAWN_VALUE + (piece - WHITE_PAWN) * KING_VALUE
    
    return (white_score, black_score)

def print_board(board, clear_screen=True):
    """Prints the provided board to the terminal, by default also clears the console"""
    if clear_screen: terminal.clear_screen()
    print("[Turn]: %s" % get_current_player(board, as_str=True).title())
    print("[Score]: White %d, Black %d\n" % get_score(board))

    for index in range(CELLS):
        x, y = index_to_coord(index)

        if x + y == 0: _print_horizontal_header()
        if x == 0: _print_vertical_header(BOARD_SIZE - y)

        piece = get_piece(board, index)
        bg_col = terminal.bg_white if (x + y) % 2 == 0 else terminal.bg_green
        if index in SELECTED: bg_col = terminal.bg_red
        elif index in TARGETS: bg_col = terminal.bg_magenta

        fg_col = terminal.fg_white if piece <= WHITE_KING else terminal.fg_black
        terminal.set_immediate_style(bg_col, fg_col)
        str_piece = PIECES_TO_STR[piece]
        print(' %s ' % str_piece, end='')

        if x == BOARD_SIZE - 1:
            _print_vertical_header(BOARD_SIZE - y)
            terminal.set_style('default')
            print('')

            if y == BOARD_SIZE - 1: _print_horizontal_header()
    
    terminal.set_style('default')
    print('')

@lru_cache(maxsize=CELLS)
def name_to_index(name):
    """Converts the provided name, such as A8, to an index on the board, such as 0"""
    name = name.upper()
    col_name = name[0]
    row_name = int(name[1:])

    x = ALPHABET.find(col_name)
    if x == -1: return -1
    y = BOARD_SIZE - row_name
    if y < 0: return -1
    return coord_to_index(x, y)    

@lru_cache(maxsize=CELLS)
def index_to_name(index):
    """Converts an index back to a human readable name"""
    x, y = index_to_coord(index)
    return '%s%d' % (ALPHABET[x], BOARD_SIZE - y)

@lru_cache(maxsize=CELLS)
def coord_to_index(x, y):
    """Returns the index associated with the provided x and y position"""
    return x + y * BOARD_SIZE

@lru_cache(maxsize=CELLS)
def index_to_coord(i):
    """Returns the 2d coordinates associated with the provided index"""
    return (i % BOARD_SIZE, i // BOARD_SIZE)

def _print_horizontal_header():
    """Prints the horizontal header, put here to prevent code repetition"""
    terminal.set_immediate_style(terminal.bg_blue, terminal.fg_gray)
    header = [' %s ' % ALPHABET[index] for index in range(BOARD_SIZE)]
    header.insert(0, '   ')
    header.append('   ')
    print("".join(header))

def _print_vertical_header(index):
    """Prints the left and right hand side headers"""
    terminal.set_immediate_style(terminal.bg_blue, terminal.fg_gray)
    print(' %d ' % index, end='')