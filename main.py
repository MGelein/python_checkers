import checkerboard
import time

def main():
    """The main entry method, this is where the code starts"""
    board = checkerboard.get_init()
    checkerboard.print_board(board)

    while True:
        sel_index = -1
        while sel_index < 0:
            moveable_pieces = [piece for piece, dest in checkerboard.get_possible_moves(board)]
            moveable_names = list(set([checkerboard.index_to_name(moveable_piece) for moveable_piece in moveable_pieces]))
            checkerboard.print_board(board)
            print("You can select: %s" % ", ".join(moveable_names))

            if len(moveable_names) > 1:
                sel_piece = input("Select a piece: ")
            else:
                sel_piece = moveable_names[0]
                time.sleep(1)

            sel_index = checkerboard.name_to_index(sel_piece)
            if sel_index not in moveable_pieces: sel_index = -1    
    
        checkerboard.clear_target()
        checkerboard.set_selected(sel_index)

        to_index = -1
        while to_index < 0:
            move_indeces = checkerboard.get_possible_moves_from(board, sel_index)
            if len(move_indeces) < 1: break
            move_names = list(set([checkerboard.index_to_name(move) for move in move_indeces]))
            for move_index in move_indeces:
                checkerboard.set_target(move_index)
            
            checkerboard.print_board(board)
            print("You can move to: %s" % ", ".join(move_names))

            if len(move_names) > 1:
                to_piece = input("Select a destination: ")
            else:
                to_piece = move_names[0]
                time.sleep(1)

            to_index = checkerboard.name_to_index(to_piece)
            if to_index not in move_indeces: to_index = -1

        checkerboard.clear_selected()
        checkerboard.clear_target()
        if to_index != -1: 
            board = checkerboard.move_piece(board, sel_index, to_index)
            if len(checkerboard.get_possible_jumps(board)) == 0:
                board = checkerboard.transfer_turn(board)

# Find the correct entry point to start running the code if this is the main module
if __name__ == '__main__':
    main()