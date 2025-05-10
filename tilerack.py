import pygame
from tile import Tile

TILE_RACK_WIDTH = 120  # Width of each tile in the rack
TILE_RACK_HEIGHT = 40  # Height of each tile
TILE_RACK_Y = 580  # Y position of the rack at the bottom of the screen
MARGIN_X = 10  # Horizontal margin between tiles

class TileRack:
    def __init__(self):
        self.tiles = []
        self.x = 10  # X position of the TileRack (start it from the left side)
        self.y = TILE_RACK_Y

    def add_tile(self, tile):
        self.tiles.append(tile)

    def draw(self, surface):
        # Draw the tiles in the rack at the bottom of the screen
        for i, tile in enumerate(self.tiles):
            tile.rect.x = self.x + (i * (TILE_RACK_WIDTH + MARGIN_X))  # Position tiles horizontally
            tile.rect.y = self.y
            tile.draw(surface)

    def get_tile_at(self, mouse_x, mouse_y):
        # Return the tile that was clicked based on mouse position
        for tile in self.tiles:
            if tile.rect.collidepoint(mouse_x, mouse_y):
                return tile
        return None
