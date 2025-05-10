import pygame

TILE_SIZE = 40
ROWS, COLS = 20, 20
GRID_COLOR = (200, 200, 200)
BG_COLOR = (255, 255, 255)

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

    def print_placed_tiles(self):
        print("Placed Tiles:")
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.grid[row][col]
                if tile:
                    print(f"Tile '{tile.letter}' at ({row}, {col})")
        print("-" * 30)
