import pygame
from tile import Tile

TILE_RACK_WIDTH = 45  # Match tile size
TILE_RACK_HEIGHT = 45
TILE_RACK_Y = 750  # Move rack lower
MARGIN_X = 8
MAX_TILES = 7

class TileRack:
    def __init__(self):
        self.tiles = []
        # Center the rack horizontally
        rack_width = MAX_TILES * (TILE_RACK_WIDTH + MARGIN_X) - MARGIN_X
        self.x = (1200 - rack_width) // 2  # Center horizontally
        self.y = TILE_RACK_Y
        self.selected_tile = None
        self.drag_start_pos = None
        self.original_pos = None

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
        # Position tiles horizontally
        for i, tile in enumerate(self.tiles):
            if tile.in_rack:
                tile.rect.x = self.x + (i * (TILE_RACK_WIDTH + MARGIN_X))
                tile.rect.y = self.y

    def draw(self, surface):
        # Draw the rack background with rounded corners
        rack_width = MAX_TILES * (TILE_RACK_WIDTH + MARGIN_X) - MARGIN_X
        rack_rect = pygame.Rect(self.x - 10, self.y - 10, 
                               rack_width + 20, 
                               TILE_RACK_HEIGHT + 20)
        pygame.draw.rect(surface, (220, 220, 220), rack_rect, border_radius=10)
        pygame.draw.rect(surface, (180, 180, 180), rack_rect, width=2, border_radius=10)
        
        # Draw the tiles
        for tile in self.tiles:
            if tile.in_rack and tile != self.selected_tile:
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
