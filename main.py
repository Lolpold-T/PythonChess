import pygame as p
import engine

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 768
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT//DIMENSION
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
MAX_FPS = 60
IMAGES = {}


def load_images():
    pieces = ["wP", "wR", "wN", "wbB", "wwB", "wK",
              "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        try:
            IMAGES[piece] = p.image.load(f"Images/{piece}.png")
        except:
            pass


def main():
    p.init()
    screen = p.display.set_mode(
        (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.RESIZABLE)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 18, False, False)
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    animate = False
    load_images()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # MOUSE HANDLER
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0]//SQUARE_SIZE
                    row = location[1]//SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2:
                        move = engine.Move(
                            player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]
            # KEY HANDLERS
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gs.undo_move()
                    move_made = True
                    animate = False

                if e.key == p.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

            if move_made:
                if animate:
                    animate_move(gs.move_log[-1], screen, gs.board, clock)
                valid_moves = gs.get_valid_moves()
                move_made = False
                animate = False

            draw_game_state(screen, gs, valid_moves,
                            square_selected, move_log_font)

            if gs.checkmate or gs.stalemate:
                game_over = True
                if gs.stalemate:
                    text = "STALEMATE"
                else:
                    text = "CHECKMATE BLACK WINS" if gs.white_to_move else "CHECKMATE WHITE WINS"
                draw_end_game_text(screen, text)

            clock.tick(MAX_FPS)
            p.display.flip()


def draw_game_state(screen, gs, valid_moves, square_selected, move_log_font):
    draw_squares(screen)
    hightlight_squares(screen, gs, valid_moves, square_selected)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, move_log_font)


def draw_squares(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row+col) % 2]
            p.draw.rect(screen, color,
                        p.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE,
                               SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece],
                            p.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE,
                                   SQUARE_SIZE, SQUARE_SIZE))


def draw_move_log(screen, gs, font):
    move_log_rect = p.Rect(
        BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = f"{str(i//2 + 1)}. "+str(move_log[i])+' '
        if i + 1 < len(move_log):
            move_string += str(move_log[i+1]) + "  "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding

    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def hightlight_squares(screen, gs, valid_moves, square_selected):
    if square_selected != ():
        row, col = square_selected
        if gs.board[row][col][0] == ('w' if gs.white_to_move else 'b'):
            # HIGHLIGHT SELECTED SQUARE
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue' if gs.white_to_move else 'red'))
            screen.blit(s, (col*SQUARE_SIZE, row*SQUARE_SIZE))
            # HIGHTLIGHT MOVES FROM SQUARE
            s.fill(p.Color('light blue' if gs.white_to_move else 'orange'))

            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col*SQUARE_SIZE,
                                    move.end_row*SQUARE_SIZE))


def animate_move(move, screen, board, clock):
    global colors
    delta_row = move.end_row - move.start_row
    delta_col = move.end_col - move.start_col
    fps = 2
    frame_count = (abs(delta_row) + abs(delta_col)) * fps
    for frame in range(frame_count+1):
        row, col = (move.start_row + delta_row*frame/frame_count,
                    move.start_col + delta_col*frame/frame_count)
        draw_squares(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQUARE_SIZE,
                            move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        # DRAW CAPTURED PIECE
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + \
                    1 if move.piece_captured[0] == 'b' else move.end_row-1
                end_square = p.Rect(move.end_col*SQUARE_SIZE,
                                    enpassant_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # DRAW MOVING PIECE
        screen.blit(IMAGES[move.piece_moved], p.Rect(
            col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 1, p.Color('Black'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_object.get_BOARD_WIDTH()/2, BOARD_HEIGHT/2 - text_object.get_BOARD_HEIGHT()/2)
    screen.blit(text_object, text_location)


if __name__ == "__main__":
    main()
