import pygame
import random
from dictionary import Dictionary

TILE_SIZE = 45
ROWS, COLS = 15, 15
GRID_COLOR = (200, 200, 200)
BG_COLOR = (240, 240, 240)
BLACK = (0, 0, 0)

# Bonus space colors
DW_COLOR = (255, 200, 200)  # Light red for double word
TW_COLOR = (255, 100, 100)  # Dark red for triple word
DL_COLOR = (200, 200, 255)  # Light blue for double letter
TL_COLOR = (100, 100, 255)  # Dark blue for triple letter

class ScrabbleBoard:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        # Center the board horizontally
        board_width = COLS * TILE_SIZE
        board_height = ROWS * TILE_SIZE
        x = (1200 - board_width) // 2  # Center horizontally
        y = 50  # Keep top margin
        self.rect = pygame.Rect(x, y, board_width, board_height)
        self.current_turn_tiles = set()
        self.bonus_spaces = self._initialize_bonus_spaces()
        self._create_static_board()
        self.selected_tile = None
        self.drag_start_pos = None
        self.dictionary = Dictionary()

    def _initialize_bonus_spaces(self):
        bonus_spaces = {}
        center = ROWS // 2
        
        # Triple Word (TW) - symmetrical star pattern
        tw_positions = [
            (3, 3), (3, COLS-4),
            (center, center),
            (ROWS-4, 3), (ROWS-4, COLS-4)
        ]
        for pos in tw_positions:
            bonus_spaces[pos] = ('TW', TW_COLOR)
        
        # Double Word (DW) - symmetrical diamond pattern
        dw_positions = [
            (1, center),
            (center, 1), (center, COLS-2),
            (ROWS-2, center),
            (5, 5), (5, COLS-6),
            (ROWS-6, 5), (ROWS-6, COLS-6)
        ]
        for pos in dw_positions:
            bonus_spaces[pos] = ('DW', DW_COLOR)
        
        # Triple Letter (TL) - symmetrical cross pattern
        tl_positions = [
            (2, 2), (2, COLS-3),
            (2, center),
            (center, 2), (center, COLS-3),
            (ROWS-3, 2), (ROWS-3, center), (ROWS-3, COLS-3)
        ]
        for pos in tl_positions:
            bonus_spaces[pos] = ('TL', TL_COLOR)
        
        # Double Letter (DL) - symmetrical corner pattern
        dl_positions = [
            (0, 4), (0, COLS-5),
            (4, 0), (4, COLS-1),
            (4, 4), (4, COLS-5),
            (ROWS-5, 0), (ROWS-5, COLS-1),
            (ROWS-5, 4), (ROWS-5, COLS-5),
            (ROWS-1, 4), (ROWS-1, COLS-5)
        ]
        for pos in dl_positions:
            bonus_spaces[pos] = ('DL', DL_COLOR)
        
        return bonus_spaces

    def _create_static_board(self):
        # Create a surface for the static board elements
        self.static_surface = pygame.Surface((COLS * TILE_SIZE, ROWS * TILE_SIZE))
        self.static_surface.fill(BG_COLOR)
        
        # Draw grid lines
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Draw bonus spaces
                if (row, col) in self.bonus_spaces:
                    bonus_type, color = self.bonus_spaces[(row, col)]
                    pygame.draw.rect(self.static_surface, color, rect)
                    
                    # Draw bonus text with better font
                    font = pygame.font.SysFont('Arial', 16, bold=True)
                    text = font.render(bonus_type, True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    self.static_surface.blit(text, text_rect)
                else:
                    # Draw regular grid cell
                    pygame.draw.rect(self.static_surface, GRID_COLOR, rect, 1)

    def draw(self, surface):
        # Draw the static board elements
        surface.blit(self.static_surface, self.rect.topleft)
        
        # Draw only the placed tiles
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col]:
                    self.grid[row][col].draw(surface)

    def snap_position(self, x, y):
        # Check if the position is within the board bounds
        if not self.rect.collidepoint(x, y):
            return None
            
        # Calculate grid position relative to board's top-left corner
        rel_x = x - self.rect.x
        rel_y = y - self.rect.y
        
        # Calculate the exact grid position
        col = int(rel_x / TILE_SIZE)
        row = int(rel_y / TILE_SIZE)
        
        # Ensure we're within bounds
        if 0 <= row < ROWS and 0 <= col < COLS:
            return row, col
        return None

    def can_place(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS and self.grid[row][col] is None

    def place_tile(self, tile, row, col):
        if self.can_place(row, col):
            # Remove the tile from its previous position if it was placed
            if tile.placed_cell:
                old_row, old_col = tile.placed_cell
                if self.grid[old_row][old_col] == tile:
                    self.grid[old_row][old_col] = None
                    self.current_turn_tiles.discard(tile)
            
            # Place the tile in the new position
            self.grid[row][col] = tile
            
            # Calculate exact pixel position for snapping
            exact_x = self.rect.x + (col * TILE_SIZE)
            exact_y = self.rect.y + (row * TILE_SIZE)
            tile.rect.topleft = (exact_x, exact_y)
            
            tile.place(row, col)
            self.current_turn_tiles.add(tile)
            tile.in_rack = False
            return True
        return False

    def remove_tile(self, tile):
        if tile.placed_cell:
            row, col = tile.placed_cell
            if self.grid[row][col] == tile:
                self.grid[row][col] = None
                self.current_turn_tiles.discard(tile)
            tile.unplace()
            return True
        return False

    def get_tile_at(self, x, y):
        # Return the tile at the given position if it's from the current turn
        grid_pos = self.snap_position(x, y)
        if grid_pos:
            row, col = grid_pos
            if 0 <= row < ROWS and 0 <= col < COLS:
                tile = self.grid[row][col]
                if tile and tile in self.current_turn_tiles:
                    return tile
        return None

    def start_drag(self, x, y):
        """Start dragging a tile from the board."""
        self.selected_tile = self.get_tile_at(x, y)
        if self.selected_tile:
            self.drag_start_pos = (x, y)
            return True
        return False

    def update_drag(self, x, y):
        """Update the position of the dragged tile."""
        if self.selected_tile:
            # Calculate the drag offset
            dx = x - self.drag_start_pos[0]
            dy = y - self.drag_start_pos[1]
            
            # Update tile position
            self.selected_tile.rect.x += dx
            self.selected_tile.rect.y += dy
            
            # Update drag start position
            self.drag_start_pos = (x, y)

    def end_drag(self, x, y):
        """End dragging a tile."""
        if self.selected_tile:
            # If the tile is dragged outside the board, return it to the rack
            if not self.rect.collidepoint(x, y):
                self.remove_tile(self.selected_tile)
                self.selected_tile = None
                self.drag_start_pos = None
                return True
            self.selected_tile = None
            self.drag_start_pos = None
        return False

    def get_word_at(self, row, col, horizontal=True):
        """Get the word formed at the given position, including tiles from previous turns."""
        word = []
        if horizontal:
            # Check left
            c = col
            while c >= 0 and self.grid[row][c]:
                tile = self.grid[row][c]
                # Use chosen_letter for blank tiles
                letter = tile.chosen_letter if tile.is_blank and tile.chosen_letter else tile.letter
                word.insert(0, letter)
                c -= 1
            # Check right
            c = col + 1
            while c < COLS and self.grid[row][c]:
                tile = self.grid[row][c]
                # Use chosen_letter for blank tiles
                letter = tile.chosen_letter if tile.is_blank and tile.chosen_letter else tile.letter
                word.append(letter)
                c += 1
        else:
            # Check up
            r = row
            while r >= 0 and self.grid[r][col]:
                tile = self.grid[r][col]
                # Use chosen_letter for blank tiles
                letter = tile.chosen_letter if tile.is_blank and tile.chosen_letter else tile.letter
                word.insert(0, letter)
                r -= 1
            # Check down
            r = row + 1
            while r < ROWS and self.grid[r][col]:
                tile = self.grid[r][col]
                # Use chosen_letter for blank tiles
                letter = tile.chosen_letter if tile.is_blank and tile.chosen_letter else tile.letter
                word.append(letter)
                r += 1
        return ''.join(word)

    def validate_current_turn(self):
        """Validate that the current turn forms valid words."""
        if not self.current_turn_tiles:
            return False, "No tiles placed in this turn"

        # Get all positions of tiles placed in current turn
        positions = [(tile.placed_cell[0], tile.placed_cell[1]) for tile in self.current_turn_tiles]
        
        # Check if tiles are contiguous
        if not self._are_tiles_contiguous(positions):
            return False, "Tiles must be placed contiguously"

        # Get the main word (horizontal or vertical)
        main_word = self._get_main_word(positions)
        if not main_word:
            return False, "No valid word formed"

        # Check if the main word is valid
        if not self.dictionary.is_valid_word(main_word):
            return False, f"'{main_word}' is not a valid word"

        # Check all crossing words
        for row, col in positions:
            # Check horizontal word
            h_word = self.get_word_at(row, col, True)
            if len(h_word) > 1 and not self.dictionary.is_valid_word(h_word):
                return False, f"'{h_word}' is not a valid word"
            
            # Check vertical word
            v_word = self.get_word_at(row, col, False)
            if len(v_word) > 1 and not self.dictionary.is_valid_word(v_word):
                return False, f"'{v_word}' is not a valid word"

        return True, "Valid word(s) formed"

    def _are_tiles_contiguous(self, positions):
        """Check if the tiles form a contiguous word when combined with existing tiles."""
        if not positions:
            return False

        # Get all positions that have tiles (both placed and existing)
        all_positions = set()
        for row, col in positions:
            # Add the current position
            all_positions.add((row, col))
            
            # Check for existing tiles in all directions
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                r, c = row + dr, col + dc
                if 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c]:
                    all_positions.add((r, c))

        # Check if all positions are in a line
        rows = [pos[0] for pos in all_positions]
        cols = [pos[1] for pos in all_positions]
        
        # Check if all tiles are in the same row
        if len(set(rows)) == 1:
            # Check if columns are contiguous
            cols.sort()
            return cols[-1] - cols[0] == len(cols) - 1
        
        # Check if all tiles are in the same column
        if len(set(cols)) == 1:
            # Check if rows are contiguous
            rows.sort()
            return rows[-1] - rows[0] == len(rows) - 1
        
        return False

    def _get_main_word(self, positions):
        """Get the main word formed by the current turn tiles."""
        if not positions:
            return None

        # Determine if the word is horizontal or vertical
        rows = [pos[0] for pos in positions]
        cols = [pos[1] for pos in positions]
        
        if len(set(rows)) == 1:  # Horizontal word
            positions.sort(key=lambda x: x[1])  # Sort by column
            return self.get_word_at(positions[0][0], positions[0][1], True)
        elif len(set(cols)) == 1:  # Vertical word
            positions.sort(key=lambda x: x[0])  # Sort by row
            return self.get_word_at(positions[0][0], positions[0][1], False)
        
        return None

    def end_turn(self):
        """End the current turn, validating the words first."""
        valid, message = self.validate_current_turn()
        if not valid:
            # If invalid, just return the error message without removing tiles
            return False, message, 0
        
        # Get the count of placed tiles before clearing
        placed_tiles_count = len(self.current_turn_tiles)
        return True, "Turn completed successfully", placed_tiles_count

    def get_bonus(self, row, col):
        # Return the bonus type for a given position
        return self.bonus_spaces.get((row, col), None)

    def print_placed_tiles(self):
        print("Placed Tiles:")
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.grid[row][col]
                if tile:
                    print(f"Tile '{tile.letter}' at ({row}, {col})")
        print("-" * 30)