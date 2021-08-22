
class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wbB", "wQ", "wK", "wwB", "wN", "wR"],
        ]
        self.move_functions = {'P': self.get_pawn_moves,
                               'R': self.get_rook_moves,
                               'B': self.get_bishop_moves,
                               'N': self.get_knight_moves,
                               'Q': self.get_queen_moves,
                               'K': self.get_king_moves
                               }
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = ()
        self.prev_move = None
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castilng_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(
            self.current_castilng_right.wks, self.current_castilng_right.bks,
            self.current_castilng_right.wqs, self.current_castilng_right.bqs)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.switch_turns()
        # UPDATE KING LOCATION
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # PROMOTE TO QUEEN
        if move.is_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # EN PASSANT
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'

        # UPDATE EN PASSANT VARIABLE
        if move.piece_moved[-1] == 'P' and abs(move.start_row-move.end_row) == 2:
            self.enpassant_possible = (
                (move.start_row + move.end_row)//2, move.start_col)
        else:
            self.enpassant_possible = ()

        self.enpassant_possible_log.append(self.enpassant_possible)

        # CASTLE MOVE
        if move.is_castle_move:
            # KINGSIDE
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col -
                                         1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = "--"
            # QUEENSIDE
            else:
                self.board[move.end_row][move.end_col +
                                         1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = "--"

        # UPDATE CASTLING RIGHTS
        self.update_castle_rights(move)

        self.castle_rights_log.append(CastleRights(
            self.current_castilng_right.wks, self.current_castilng_right.bks,
            self.current_castilng_right.wqs, self.current_castilng_right.bqs))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()

            self.prev_move = move
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.switch_turns()
            # UNDO KING POSITION
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)

            # UNDO EN PASSANT
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # UNDO CASTLING RIGHTS
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castilng_right = CastleRights(
                new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)

            # UNDO CASTLE MOVE
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col +
                                             1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = "--"
                else:
                    self.board[move.end_row][move.end_col -
                                             2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = "--"

            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castilng_right.wks = False
            self.current_castilng_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castilng_right.bks = False
            self.current_castilng_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castilng_right.wqs = False
                elif move.start_col == 7:
                    self.current_castilng_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castilng_right.bqs = False
                elif move.start_col == 7:
                    self.current_castilng_right.bks = False

        # IF ROOK IS CAPTURED
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castilng_right.wqs = False
                elif move.end_col == 7:
                    self.current_castilng_right.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castilng_right.bqs = False
                elif move.end_col == 7:
                    self.current_castilng_right.bks = False

    def get_valid_moves(self):
        # SAVE VALUES BEFORE CHANGING
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(
            self.current_castilng_right.wks, self.current_castilng_right.bks,
            self.current_castilng_right.wqs, self.current_castilng_right.bqs)
        # GENERATE ALL POSSIBLE MOVES
        moves = self.get_all_possible_moves()
        # MAKE ALL THOSE MOVES
        # TODO: DON'T MAKE THESE UPDATE THE STATE
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.switch_turns()
            if self.in_check():
                moves.remove(moves[i])
            self.switch_turns()
            self.undo_move()

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True

         # GET CASTLE MOVES
        if self.white_to_move:
            self.get_castle_moves(
                self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(
                self.black_king_location[0], self.black_king_location[1], moves)

        self.enpassant_possible = temp_enpassant_possible
        self.current_castilng_right = temp_castle_rights
        return moves

    def switch_turns(self):
        self.white_to_move = not self.white_to_move

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row, col):
        self.switch_turns()
        opponent_moves = self.get_all_possible_moves()
        self.switch_turns()
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][-1]
                    self.move_functions[piece](row, col, moves)
        return moves

    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:
            if self.board[row-1][col] == "--":
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--":
                    moves.append(Move((row, col), (row-2, col), self.board))
            if col-1 >= 0:
                if self.board[row-1][col-1][0] == 'b':
                    moves.append(
                        Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enpassant_possible:
                    moves.append(
                        Move((row, col), (row-1, col-1), self.board, is_enpassant_move=True))
            if col+1 < len(self.board):
                if self.board[row-1][col+1][0] == 'b':
                    moves.append(
                        Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enpassant_possible:
                    moves.append(
                        Move((row, col), (row-1, col+1), self.board, is_enpassant_move=True))
        else:
            if self.board[row+1][col] == "--":
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--":
                    moves.append(Move((row, col), (row+2, col), self.board))
            if col-1 >= 0:
                if self.board[row+1][col-1][0] == 'w':
                    moves.append(
                        Move((row, col), (row+1, col-1), self.board))
                elif (row+1, col-1) == self.enpassant_possible:
                    moves.append(
                        Move((row, col), (row+1, col-1), self.board, is_enpassant_move=True))
            if col+1 < len(self.board):
                if self.board[row+1][col+1][0] == 'w':
                    moves.append(
                        Move((row, col), (row+1, col+1), self.board))
                elif (row+1, col+1) == self.enpassant_possible:
                    moves.append(
                        Move((row, col), (row+1, col+1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        n = len(self.board)
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, n):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < n and 0 <= end_col < n:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_bishop_moves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        n = len(self.board)
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, n):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < n and 0 <= end_col < n:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, row, col, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        n = len(self.board)
        for m in knight_moves:
            end_row = row + m[0]
            end_col = col + m[1]
            if 0 <= end_row < n and 0 <= end_col < n:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(
                        Move((row, col), (end_row, end_col), self.board))

    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = 'w' if self.white_to_move else 'b'

        for i in range(8):
            end_row = row + king_moves[i][0]
            end_col = col + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(
                        Move((row, col), (end_row, end_col), self.board))

    def get_castle_moves(self, row, col, moves):
        if self.square_under_attack(row, col):
            return
        if (self.white_to_move and self.current_castilng_right.wks) or (not self.white_to_move and self.current_castilng_right.bks):
            self.get_kingside_castle_moves(row, col, moves)
        if (self.white_to_move and self.current_castilng_right.wqs) or (not self.white_to_move and self.current_castilng_right.bqs):
            self.get_queenside_castle_moves(row, col, moves)

    def get_kingside_castle_moves(self, row, col, moves):
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            if not self.square_under_attack(row, col+1) and not self.square_under_attack(row, col+2):
                moves.append(Move((row, col), (row, col+2),
                                  self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, col, moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3]:
            if not self.square_under_attack(row, col-1) and not self.square_under_attack(row, col-2):
                moves.append(Move((row, col), (row, col-2),
                                  self.board, is_castle_move=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {val: key for key, val in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {val: key for key, val in files_to_cols.items()}

    def __init__(self, start, end, board, is_enpassant_move=False, is_castle_move=False) -> None:
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # PAWN PROMOTION
        self.is_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (
            self.piece_moved == 'bP' and self.end_row == 7)

        # EN PASSANT
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        # CAPTURE
        self.is_capture = self.piece_captured != "--"

        # CASTLING
        self.is_castle_move = is_castle_move

        self.move_id = self.start_row * 1000 + \
            self.start_col*100 + self.end_row*10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def __str__(self):
        # CASTLE MOVE
        if self.is_castle_move:
            # "O-O" KINGSIDE
            # "O-O-O" QUEENSIDE
            return "O-O" if self.end_col == 6 else "O-O-O"

        end_square = self.get_rank_file(self.end_row, self.end_col)
        # PAWN MOVES
        if self.piece_moved[-1] == 'P':
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square

        move_string = self.piece_moved[-1]
        if self.is_capture:
            move_string += "x"+end_square
        else:
            move_string += end_square

        # MISSING PAWN PROMOTIONS
        # MISSING BOTH KNIGHTS CAN GO TO SAME TILE
        # ADDING + FOR CHECK MOVE AND # FOR CHECKMATE MOVED

        # PIECEMOVES
        return move_string

    def get_chess_notation(self):
        # TODO: make better chess notation
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
