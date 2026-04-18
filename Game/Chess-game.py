# Re-create the file since the previous state was reset.
code = r""
import sys
import os
import pygame
from typing import List, Tuple, Optional

# ---------- Config ----------
WIDTH, HEIGHT = 640, 640
BOARD_SIZE = 8
SQ = WIDTH // BOARD_SIZE
FPS = 60

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
MOVE_DOT = (40, 40, 40)
CHECK_RED = (220, 20, 60)
TEXT = (20, 20, 20)
PANEL_BG = (235, 235, 235)

IMAGES_DIR = "images"  # Put 12 PNGs here named wP.png ... bK.png

# ---------- Model ----------

# Pieces are represented as two-char strings: Color + Type, e.g., 'wK', 'bQ'.
# Empty squares are None.

def initial_board() -> List[List[Optional[str]]]:
    # Using standard chess starting position
    board = [[None for _ in range(8)] for _ in range(8)]
    # Black
    board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
    board[1] = ['bP'] * 8
    # Empty
    for r in range(2, 6):
        board[r] = [None] * 8
    # White
    board[6] = ['wP'] * 8
    board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    return board

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def color_of(piece: Optional[str]) -> Optional[str]:
    if piece is None: return None
    return piece[0]

def type_of(piece: Optional[str]) -> Optional[str]:
    if piece is None: return None
    return piece[1]

def find_king(board, color) -> Tuple[int, int]:
    for r in range(8):
        for c in range(8):
            if board[r][c] == color + 'K':
                return r, c
    return -1, -1

# ---- Move generation helpers ----

DIRS_BISHOP = [(-1,-1), (-1,1), (1,-1), (1,1)]
DIRS_ROOK = [(-1,0), (1,0), (0,-1), (0,1)]
DIRS_KNIGHT = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
DIRS_KING = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

def ray_moves(board, r, c, dirs, color):
    moves = []
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] is None:
                moves.append((nr, nc))
            else:
                if color_of(board[nr][nc]) != color:
                    moves.append((nr, nc))
                break
            nr += dr; nc += dc
    return moves

def pseudo_moves_for_piece(board, r, c) -> List[Tuple[int,int]]:
    piece = board[r][c]
    if not piece: return []
    color = color_of(piece)
    kind = type_of(piece)

    moves = []
    if kind == 'P':
        dir_ = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        # forward
        fr, fc = r + dir_, c
        if in_bounds(fr, fc) and board[fr][fc] is None:
            moves.append((fr, fc))
            # double push
            fr2 = r + 2*dir_
            if r == start_row and board[fr2][fc] is None:
                moves.append((fr2, fc))
        # captures
        for dc in (-1, 1):
            cr, cc = r + dir_, c + dc
            if in_bounds(cr, cc) and board[cr][cc] is not None and color_of(board[cr][cc]) != color:
                moves.append((cr, cc))
        # (No en passant to keep this simple)
    elif kind == 'N':
        for dr, dc in DIRS_KNIGHT:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and color_of(board[nr][nc]) != color:
                moves.append((nr, nc))
    elif kind == 'B':
        moves.extend(ray_moves(board, r, c, DIRS_BISHOP, color))
    elif kind == 'R':
        moves.extend(ray_moves(board, r, c, DIRS_ROOK, color))
    elif kind == 'Q':
        moves.extend(ray_moves(board, r, c, DIRS_BISHOP + DIRS_ROOK, color))
    elif kind == 'K':
        for dr, dc in DIRS_KING:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and color_of(board[nr][nc]) != color:
                moves.append((nr, nc))
        # (No castling to keep this simple)
    return moves

def is_square_attacked(board, r, c, by_color) -> bool:
    # Check knight
    for dr, dc in DIRS_KNIGHT:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == by_color + 'N':
            return True
    # Check king
    for dr, dc in DIRS_KING:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == by_color + 'K':
            return True
    # Check bishop/queen diagonals
    for dr, dc in DIRS_BISHOP:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            p = board[nr][nc]
            if p is not None:
                if color_of(p) == by_color and type_of(p) in ('B','Q'):
                    return True
                break
            nr += dr; nc += dc
    # Check rook/queen straights
    for dr, dc in DIRS_ROOK:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            p = board[nr][nc]
            if p is not None:
                if color_of(p) == by_color and type_of(p) in ('R','Q'):
                    return True
                break
            nr += dr; nc += dc
    # Check pawns
    pawn_dir = -1 if by_color == 'w' else 1
    for dc in (-1, 1):
        nr, nc = r + pawn_dir, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == by_color + 'P':
            return True
    return False

def make_move(board, src, dst) -> List[List[Optional[str]]]:
    r1, c1 = src; r2, c2 = dst
    newb = [row[:] for row in board]
    piece = newb[r1][c1]
    newb[r1][c1] = None
    # Pawn promotion (auto-queen)
    if type_of(piece) == 'P' and (r2 == 0 or r2 == 7):
        newb[r2][c2] = color_of(piece) + 'Q'
    else:
        newb[r2][c2] = piece
    return newb

def legal_moves(board, r, c) -> List[Tuple[int,int]]:
    piece = board[r][c]
    if not piece: return []
    color = color_of(piece)
    moves = []
    for (nr, nc) in pseudo_moves_for_piece(board, r, c):
        nb = make_move(board, (r,c), (nr,nc))
        kr, kc = find_king(nb, color)
        if not is_square_attacked(nb, kr, kc, 'w' if color == 'b' else 'b'):
            moves.append((nr, nc))
    return moves

def has_any_legal(board, color) -> bool:
    for r in range(8):
        for c in range(8):
            if board[r][c] and color_of(board[r][c]) == color:
                if legal_moves(board, r, c):
                    return True
    return False

def in_check(board, color) -> bool:
    kr, kc = find_king(board, color)
    return is_square_attacked(board, kr, kc, 'w' if color == 'b' else 'b')

# ---------- View / Controller ----------

class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Chess (2-Player) - PNG Pieces Support')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 64))  # small panel below
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        # Try a larger font for Unicode chess glyphs as fallback
        self.glyph_font = pygame.font.SysFont("dejavusans", 44)
        self.board = initial_board()
        self.turn = 'w'
        self.selected = None
        self.moves_cache: List[Tuple[int,int]] = []
        self.game_over = False
        self.result_text = ""

        # Load images (if present). Missing files are ignored; fallback will be used.
        self.images = {}
        pieces = ['wP','wR','wN','wB','wQ','wK','bP','bR','bN','bB','bQ','bK']
        for p in pieces:
            path = os.path.join(IMAGES_DIR, f"{p}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.images[p] = pygame.transform.smoothscale(img, (SQ, SQ))
                except Exception as e:
                    # If loading fails, skip image for this piece
                    print(f"Failed to load {path}: {e}")
            # If image missing, we simply won't add to dict => fallback

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                rect = pygame.Rect(c*SQ, r*SQ, SQ, SQ)
                pygame.draw.rect(self.screen, color, rect)

        # highlight selected
        if self.selected:
            r, c = self.selected
            pygame.draw.rect(self.screen, HIGHLIGHT, (c*SQ, r*SQ, SQ, SQ), 6)

        # Draw check highlight on king if in check
        if in_check(self.board, self.turn):
            kr, kc = find_king(self.board, self.turn)
            pygame.draw.rect(self.screen, CHECK_RED, (kc*SQ+4, kr*SQ+4, SQ-8, SQ-8), 4)

        # draw pieces
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    self.draw_piece(p, r, c)

        # draw possible moves
        for (mr, mc) in self.moves_cache:
            center = (mc*SQ + SQ//2, mr*SQ + SQ//2)
            pygame.draw.circle(self.screen, MOVE_DOT, center, 8)

        # panel
        pygame.draw.rect(self.screen, PANEL_BG, (0, HEIGHT, WIDTH, 64))
        status = f"Turn: {'White' if self.turn=='w' else 'Black'}"
        if self.game_over:
            status = self.result_text
        text_surface = self.font.render(status, True, TEXT)
        self.screen.blit(text_surface, (10, HEIGHT + 16))

        tip = "PNG pieces: put 12 files in ./images (wP..wK, bP..bK). Pawn auto-queen. No castling/en passant."
        tip_surface = pygame.font.SysFont(None, 24).render(tip, True, TEXT)
        self.screen.blit(tip_surface, (10, HEIGHT + 40))

    def draw_piece(self, piece, r, c):
        rect = pygame.Rect(c*SQ, r*SQ, SQ, SQ)
        img = self.images.get(piece)
        if img:
            self.screen.blit(img, rect.topleft)
            return

        # Fallback to Unicode glyphs
        color = color_of(piece)
        kind = type_of(piece)
        glyphs = {
            ('w','K'): '\u2654', ('w','Q'): '\u2655', ('w','R'): '\u2656',
            ('w','B'): '\u2657', ('w','N'): '\u2658', ('w','P'): '\u2659',
            ('b','K'): '\u265A', ('b','Q'): '\u265B', ('b','R'): '\u265C',
            ('b','B'): '\u265D', ('b','N'): '\u265E', ('b','P'): '\u265F',
        }
        ch = glyphs.get((color, kind), None)
        if ch:
            surf = self.glyph_font.render(ch, True, (0,0,0))
            sr = surf.get_rect(center=rect.center)
            self.screen.blit(surf, sr)
        else:
            # Final fallback: text label like 'wK'
            label = self.font.render(piece, True, (0,0,0))
            lr = label.get_rect(center=rect.center)
            self.screen.blit(label, lr)

    def handle_click(self, pos):
        if self.game_over:
            return
        x, y = pos
        if y >= HEIGHT:  # clicked panel
            return
        c = x // SQ
        r = y // SQ
        if not in_bounds(r, c):
            return

        p = self.board[r][c]
        if self.selected is None:
            # select if it is our piece
            if p and color_of(p) == self.turn:
                self.selected = (r, c)
                self.moves_cache = legal_moves(self.board, r, c)
        else:
            sr, sc = self.selected
            if (r, c) == (sr, sc):
                # deselect
                self.selected = None
                self.moves_cache = []
                return
            # If destination is legal
            if (r, c) in self.moves_cache:
                self.board = make_move(self.board, (sr, sc), (r, c))
                # Switch turn
                self.turn = 'b' if self.turn == 'w' else 'w'
                self.selected = None
                self.moves_cache = []

                # Check for end conditions
                if in_check(self.board, self.turn) and not has_any_legal(self.board, self.turn):
                    # Checkmate
                    winner = 'White' if self.turn == 'b' else 'Black'
                    self.result_text = f"Checkmate! {winner} wins."
                    self.game_over = True
                elif not in_check(self.board, self.turn) and not has_any_legal(self.board, self.turn):
                    # Stalemate
                    self.result_text = "Stalemate. Draw."
                    self.game_over = True
            else:
                # Re-select if clicked own piece
                if p and color_of(p) == self.turn:
                    self.selected = (r, c)
                    self.moves_cache = legal_moves(self.board, r, c)
                else:
                    # invalid: deselect
                    self.selected = None
                    self.moves_cache = []

    def loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.screen.fill((0,0,0))
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    ChessGame().loop()

