import pygame
from tile import Tile

TILE_RACK_WIDTH = 40  # Width of each tile in the rack
TILE_RACK_HEIGHT = 40  # Height of each tile
TILE_RACK_Y = 580  # Y position of the rack at the bottom of the screen
MARGIN_X = 5  # Horizontal margin between tiles
MAX_TILES = 7  # Maximum number of tiles in the rack

class TileRack:
    def __init__(self):
        self.tiles = []
        self.x = 10  # X position of the TileRack (start it from the left side)
        self.y = TILE_RACK_Y
        self.selected_tile = None
        self.drag_start_pos = None
        self.original_pos = None  # Store original position of dragged tile

    def add_tile(self, tile):
        if len(self.tiles) < MAX_TILES:
            print(f"Adding tile {tile.letter} to rack. Current count: {len(self.tiles)}")
            tile.in_rack = True  # Ensure tile is marked as in rack
            self.tiles.append(tile)
            self._update_tile_positions()
            print(f"Tile added. New count: {len(self.tiles)}")
            return True
        print(f"Cannot add tile. Rack is full ({len(self.tiles)} tiles)")
        return False

    def _update_tile_positions(self):
        # Calculate total width of all tiles with margins
        total_width = len(self.tiles) * (TILE_RACK_WIDTH + MARGIN_X) - MARGIN_X
        # Calculate starting x position to center the tiles
        start_x = self.x + (800 - total_width) // 2  # 800 is the screen width
        
        # Position tiles horizontally
        for i, tile in enumerate(self.tiles):
            if tile.in_rack:  # Only update position if tile is in rack
                tile.rect.x = start_x + (i * (TILE_RACK_WIDTH + MARGIN_X))
                tile.rect.y = self.y

    def draw(self, surface):
        # Draw the rack background
        rack_rect = pygame.Rect(self.x, self.y, 800, TILE_RACK_HEIGHT)
        pygame.draw.rect(surface, (200, 200, 200), rack_rect)
        
        # Draw the tiles
        for tile in self.tiles:
            if tile.in_rack and tile != self.selected_tile:  # Only draw rack tiles
                tile.draw(surface)
        
        # Draw the selected tile last (on top)
        if self.selected_tile and self.selected_tile.in_rack:
            self.selected_tile.draw(surface)

    def get_tile_at(self, mouse_x, mouse_y):
        # Return the tile that was clicked based on mouse position
        for tile in self.tiles:
            if tile.in_rack and tile.rect.collidepoint(mouse_x, mouse_y):
                return tile
        return None

    def start_drag(self, mouse_x, mouse_y):
        self.selected_tile = self.get_tile_at(mouse_x, mouse_y)
        if self.selected_tile:
            self.drag_start_pos = (mouse_x, mouse_y)
            # Store the original position
            self.original_pos = (self.selected_tile.rect.x, self.selected_tile.rect.y)
            return True
        return False

    def update_drag(self, mouse_x, mouse_y):
        if self.selected_tile:
            # Calculate the drag offset
            dx = mouse_x - self.drag_start_pos[0]
            dy = mouse_y - self.drag_start_pos[1]
            
            # Update tile position
            self.selected_tile.rect.x += dx
            self.selected_tile.rect.y += dy
            
            # Update drag start position
            self.drag_start_pos = (mouse_x, mouse_y)

    def end_drag(self, pos):
        if self.selected_tile:
            # Check if the tile was placed on the board
            if not self.selected_tile.placed_cell:
                # If not placed on board, return to rack
                self.selected_tile.rect.topleft = self.original_pos
                self.selected_tile.in_rack = True
            else:
                # If placed on board, remove from rack if it's still there
                if self.selected_tile in self.tiles:
                    self.tiles.remove(self.selected_tile)
                    self.selected_tile.in_rack = False
                    print(f"Tile removed from rack. Remaining tiles: {len(self.tiles)}")
            self.selected_tile = None
            self.drag_start_pos = None
            self.original_pos = None
            self._update_tile_positions()

    def remove_tile(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)
            self._update_tile_positions()
