import pygame
import sys
from board import ScrabbleBoard, TILE_SIZE, ROWS as BOARD_SIZE
from tilebag import TileBag
from tilerack import TileRack
from scoring import ScrabbleScoring
from tile import Tile

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
ERROR_COLOR = (255, 0, 0)
SUCCESS_COLOR = (0, 255, 0)
LIGHT_BLUE = (200, 200, 255)
BOARD_BG = (240, 240, 240)
RACK_BG = (220, 220, 220)

class ScrabbleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Scrabble")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.board = ScrabbleBoard()
        self.tile_bag = TileBag()
        self.tile_rack = TileRack()
        self.scoring = ScrabbleScoring()
        
        # Initialize buttons
        self.end_turn_button = pygame.Rect(SCREEN_WIDTH - 150, 50, 120, 40)
        self.replace_letter_button = pygame.Rect(SCREEN_WIDTH - 150, 100, 120, 40)
        self.button_font = pygame.font.SysFont(None, 30)
        self.message_font = pygame.font.SysFont(None, 24)
        
        # Track currently dragged tile
        self.dragged_tile = None
        self.drag_start_pos = None
        self.original_pos = None
        
        # Track double click
        self.last_click_time = 0
        self.last_click_pos = None
        self.double_click_delay = 500  # milliseconds
        self.last_clicked_tile = None  # Track the last clicked tile
        
        # Message display
        self.message = ""
        self.message_color = BLACK
        self.message_timer = 0
        
        # Game state
        self.player_score = 0
        self.selected_tile_for_replacement = None
        
        # Blank tile selection
        self.blank_tile_selection = None
        # Position the blank tile selection area in the center of the screen
        self.blank_tile_rect = pygame.Rect(
            (SCREEN_WIDTH - 300) // 2,  # Center horizontally
            (SCREEN_HEIGHT - 300) // 2,  # Center vertically
            300,  # Width
            300   # Height
        )
        self.blank_tile_buttons = []
        self._initialize_blank_tile_buttons()
        
        # Fill the rack with initial tiles
        self.fill_rack()

    def _initialize_blank_tile_buttons(self):
        """Initialize the buttons for blank tile letter selection."""
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        button_width = 35
        button_height = 35
        buttons_per_row = 7
        start_x = self.blank_tile_rect.x + 10  # Add padding
        start_y = self.blank_tile_rect.y + 50  # Increased padding to avoid text overlap
        
        for i, letter in enumerate(letters):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + (col * (button_width + 5))  # Add spacing between buttons
            y = start_y + (row * (button_height + 5))  # Add spacing between rows
            self.blank_tile_buttons.append({
                'letter': letter,
                'rect': pygame.Rect(x, y, button_width, button_height)
            })

    def show_message(self, message, color=BLACK, duration=2000):
        self.message = message
        self.message_color = color
        self.message_timer = pygame.time.get_ticks() + duration

    def fill_rack(self):
        # Debug: Add a blank tile first
        blank_tile = Tile('_', 0, 0, 0)
        self.tile_rack.add_tile(blank_tile)
        
        # Fill the rack up to 7 tiles
        while len(self.tile_rack.tiles) < 7:
            tile = self.tile_bag.draw_tile()
            if tile:
                self.tile_rack.add_tile(tile)
            else:
                break  # No more tiles in the bag

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    current_time = pygame.time.get_ticks()
                    
                    # Check if end turn button was clicked
                    if self.end_turn_button.collidepoint(event.pos):
                        success, message = self.end_turn()
                        if success:
                            self.show_message(message, SUCCESS_COLOR)
                        else:
                            self.show_message(message, ERROR_COLOR)
                        return True
                    
                    # Check if replace letter button was clicked
                    if self.replace_letter_button.collidepoint(event.pos):
                        if self.selected_tile_for_replacement:
                            success, message = self.replace_letter()
                            if success:
                                self.show_message(message, SUCCESS_COLOR)
                            else:
                                self.show_message(message, ERROR_COLOR)
                            return True
                        else:
                            self.show_message("Select a tile to replace first", ERROR_COLOR)
                            return True
                    
                    # Check for blank tile letter selection
                    if self.blank_tile_selection:
                        for button in self.blank_tile_buttons:
                            if button['rect'].collidepoint(event.pos):
                                self.blank_tile_selection.chosen_letter = button['letter']
                                self.blank_tile_selection.update_display()
                                self.blank_tile_selection = None
                                return True
                        # If clicked outside the letter buttons, close the selection
                        if not self.blank_tile_rect.collidepoint(event.pos):
                            self.blank_tile_selection = None
                            return True
                    
                    # Check if we clicked on a tile in the rack
                    clicked_tile = self.tile_rack.get_tile_at(event.pos[0], event.pos[1])
                    if clicked_tile:
                        # Start dragging for any tile
                        if self.tile_rack.start_drag(event.pos[0], event.pos[1]):
                            self.dragged_tile = self.tile_rack.selected_tile
                            self.drag_start_pos = event.pos
                            self.original_pos = (self.dragged_tile.rect.x, self.dragged_tile.rect.y)
                            return True
                    
                    # If not in rack, check if we clicked on a tile on the board
                    board_tile = self.board.get_tile_at(event.pos[0], event.pos[1])
                    if board_tile and board_tile in self.board.current_turn_tiles:
                        self.dragged_tile = board_tile
                        self.drag_start_pos = event.pos
                        self.original_pos = (board_tile.rect.x, board_tile.rect.y)
                        self.board.remove_tile(board_tile)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    if self.dragged_tile:
                        # Try to place the tile on the board
                        mouse_x, mouse_y = event.pos
                        grid_pos = self.board.snap_position(mouse_x, mouse_y)
                        
                        if grid_pos:
                            row, col = grid_pos
                            if self.board.place_tile(self.dragged_tile, row, col):
                                # Tile was placed on board, remove from rack
                                self.tile_rack.remove_tile(self.dragged_tile)
                                print(f"Tile placed on board. Remaining tiles in rack: {len(self.tile_rack.tiles)}")
                        else:
                            # Tile was not placed on board, return to rack
                            if self.dragged_tile not in self.tile_rack.tiles:
                                self.tile_rack.add_tile(self.dragged_tile)
                            self.dragged_tile.in_rack = True
                            self.tile_rack._update_tile_positions()
                        
                        # Check if the placed tile is a blank tile
                        if self.dragged_tile.letter == '_':
                            self.blank_tile_selection = self.dragged_tile
                        
                        # Reset drag state
                        self.dragged_tile = None
                        self.drag_start_pos = None
                        self.original_pos = None
                    elif self.tile_rack.selected_tile:
                        self.tile_rack.end_drag(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                # Update drag position if dragging
                if self.dragged_tile:
                    # Calculate the drag offset
                    dx = event.pos[0] - self.drag_start_pos[0]
                    dy = event.pos[1] - self.drag_start_pos[1]
                    
                    # Update tile position
                    self.dragged_tile.rect.x += dx
                    self.dragged_tile.rect.y += dy
                    
                    # Update drag start position
                    self.drag_start_pos = event.pos
        
        return True

    def replace_letter(self):
        """Replace the selected letter with a new one from the bag."""
        if not self.selected_tile_for_replacement:
            return False, "No tile selected for replacement"
        
        # Check if player has enough points
        if self.player_score < 1:
            return False, "Not enough points to replace a letter"
        
        # Get a new tile from the bag
        new_tile = self.tile_bag.draw_tile()
        if not new_tile:
            return False, "No more tiles in the bag"
        
        # Remove the old tile and add the new one
        self.tile_rack.remove_tile(self.selected_tile_for_replacement)
        self.tile_rack.add_tile(new_tile)
        self.tile_rack._update_tile_positions()
        
        # Put the old tile back in the bag
        self.tile_bag.return_tile(self.selected_tile_for_replacement)
        
        # Deduct 1 point
        self.player_score -= 1
        
        # Reset selection
        self.selected_tile_for_replacement = None
        
        return True, f"Letter replaced! -1 point (New score: {self.player_score})"

    def end_turn(self):
        # End the current turn on the board
        success, message, placed_tiles_count = self.board.end_turn()
        if success:
            print(f"Tiles placed this turn: {placed_tiles_count}")
            
            # Calculate and update score
            turn_score = self.scoring.calculate_turn_score(self.board.current_turn_tiles, self.board)
            bonus = self.scoring.calculate_bonus(placed_tiles_count)
            total_score = turn_score + bonus
            self.player_score += total_score
            
            # Add new tiles to replace the ones that were placed
            for _ in range(placed_tiles_count):
                tile = self.tile_bag.draw_tile()
                if tile:
                    print(f"Adding tile {tile.letter} to rack")
                    self.tile_rack.add_tile(tile)
                else:
                    print("No more tiles in bag")
                    break  # No more tiles in the bag
            
            print(f"Final tiles in rack: {len(self.tile_rack.tiles)}")
            # Update the rack layout
            self.tile_rack._update_tile_positions()
            
            # Update message with score information
            message = f"Turn completed! Score: {turn_score} + {bonus} bonus = {total_score}"
            
            # Clear the current turn tiles after scoring
            self.board.current_turn_tiles.clear()
        return success, message

    def update(self):
        # Update message timer
        if self.message_timer and pygame.time.get_ticks() > self.message_timer:
            self.message = ""
            self.message_timer = 0

    def draw(self):
        # Clear the screen
        self.screen.fill(WHITE)
        
        # Draw game components
        self.board.draw(self.screen)
        self.tile_rack.draw(self.screen)
        self.tile_bag.draw(self.screen)
        
        # Draw end turn button
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER_COLOR if self.end_turn_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.end_turn_button)
        text = self.button_font.render("End Turn", True, WHITE)
        text_rect = text.get_rect(center=self.end_turn_button.center)
        self.screen.blit(text, text_rect)
        
        # Draw replace letter button
        button_color = BUTTON_HOVER_COLOR if self.replace_letter_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.replace_letter_button)
        text = self.button_font.render("Replace", True, WHITE)
        text_rect = text.get_rect(center=self.replace_letter_button.center)
        self.screen.blit(text, text_rect)
        
        # Draw blank tile selection if active
        if self.blank_tile_selection:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            # Draw the selection area
            pygame.draw.rect(self.screen, WHITE, self.blank_tile_rect)
            pygame.draw.rect(self.screen, BLACK, self.blank_tile_rect, 2)
            
            # Draw title
            title = self.button_font.render("Select Letter for Blank Tile", True, BLACK)
            title_rect = title.get_rect(centerx=self.blank_tile_rect.centerx, 
                                      top=self.blank_tile_rect.y + 10)
            self.screen.blit(title, title_rect)
            
            # Draw instructions
            instructions = self.message_font.render("Click a letter to select it", True, BLACK)
            instructions_rect = instructions.get_rect(centerx=self.blank_tile_rect.centerx,
                                                    top=title_rect.bottom + 10)
            self.screen.blit(instructions, instructions_rect)
            
            # Draw the letter buttons
            for button in self.blank_tile_buttons:
                # Draw button background
                pygame.draw.rect(self.screen, LIGHT_BLUE, button['rect'])
                pygame.draw.rect(self.screen, BLACK, button['rect'], 1)
                
                # Draw letter
                text = self.button_font.render(button['letter'], True, BLACK)
                text_rect = text.get_rect(center=button['rect'].center)
                self.screen.blit(text, text_rect)
                
                # Draw hover effect
                if button['rect'].collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (150, 150, 255), button['rect'], 2)
        
        # Draw score
        score_text = self.message_font.render(f"Score: {self.player_score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Draw message if any
        if self.message:
            message_text = self.message_font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(message_text, message_rect)
        
        # Draw dragged tile on top
        if self.dragged_tile:
            self.dragged_tile.draw(self.screen)
        
        # Update the display
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)

def main():
    game = ScrabbleGame()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
