import pygame
import sys

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 20, 20
TILE_SIZE = WIDTH // COLS
GRID_COLOR = (200, 200, 200)
BG_COLOR = (255, 255, 255)
TILE_COLOR = (173, 216, 230)
TEXT_COLOR = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrabble Board")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

class Tile:
    def __init__(self, letter, x, y):
        self.letter = letter
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(TILE_COLOR)
        text = font.render(letter, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.blit(text, text_rect)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.placed_cell = None

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class ScrabbleBoard:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def draw(self, surface):
        surface.fill(BG_COLOR)
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, GRID_COLOR, rect, 1)

    def snap_position(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            return row, col
        return None

    def can_place(self, row, col):
        return self.grid[row][col] is None

    def place_tile(self, tile, row, col):
        if self.can_place(row, col):
            self.grid[row][col] = tile
            tile.rect.topleft = (col * TILE_SIZE, row * TILE_SIZE)
            tile.placed_cell = (row, col)
            return True
        return False

    def remove_tile(self, tile):
        if tile.placed_cell:
            row, col = tile.placed_cell
            if self.grid[row][col] == tile:
                self.grid[row][col] = None
            tile.placed_cell = None

def print_placed_tiles(board):
    print("Placed Tiles:")
    for row in range(ROWS):
        for col in range(COLS):
            tile = board.grid[row][col]
            if tile:
                print(f"Tile '{tile.letter}' at ({row}, {col})")
    print("-" * 30)



# Initialize board and test tile
board = ScrabbleBoard()
tile = Tile('A', 100, 100)
tile2 = Tile('B', 200, 100)
tiles = [tile, tile2]

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for t in tiles:
                    if t.rect.collidepoint(event.pos):
                        t.dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = t.rect.x - mouse_x
                        offset_y = t.rect.y - mouse_y
                        board.remove_tile(t)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for t in tiles:
                    if t.dragging:
                        t.dragging = False
                        snap = board.snap_position(*event.pos)
                        if snap:
                            row, col = snap
                            if board.place_tile(t, row, col):
                                print_placed_tiles(board)
                            else:
                                t.rect.topleft = (100, 100)
                        else:
                            t.rect.topleft = (100, 100)

        elif event.type == pygame.MOUSEMOTION:
            for t in tiles:
                if t.dragging:
                    mouse_x, mouse_y = event.pos
                    t.rect.x = mouse_x + offset_x
                    t.rect.y = mouse_y + offset_y

    board.draw(screen)
    for t in tiles:
        t.draw(screen)

    pygame.display.flip()
    clock.tick(60)
