import pygame
import sys
from board import ScrabbleBoard, TILE_SIZE, ROWS as BOARD_SIZE
from tilebag import TileBag
from tilerack import TileRack
from scoring import ScrabbleScoring
from tile import Tile
from ai_player import AIPlayer

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
        self.ai_player = AIPlayer(self.board, self.tile_bag, self.scoring)
        
        # Initialize buttons
        self.end_turn_button = pygame.Rect(SCREEN_WIDTH - 150, 50, 120, 40)
        self.replace_button = pygame.Rect(SCREEN_WIDTH - 150, 100, 120, 40)
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
        self.is_player_turn = True  # True for player's turn, False for AI's turn
        
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
        
        # Fill the racks with initial tiles
        self.fill_rack()
        self.ai_player.fill_rack()

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
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if not self.is_player_turn:
                # AI's turn
                success, score = self.ai_player.make_move(self.player_score)
                if success:
                    print(f"AI scored {score} points")
                    # Fill player's rack
                    while len(self.tile_rack.tiles) < 7:
                        tile = self.tile_bag.draw_tile()
                        if tile:
                            self.tile_rack.add_tile(tile)
                else:
                    print("AI failed to make a move")
                self.is_player_turn = True
                return True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if a tile in the rack was clicked
                    clicked_tile = self.tile_rack.get_tile_at(event.pos[0], event.pos[1])
                    if clicked_tile:
                        # Start dragging immediately
                        if self.tile_rack.start_drag(event.pos[0], event.pos[1]):
                            self.dragged_tile = self.tile_rack.selected_tile
                            self.drag_start_pos = event.pos
                            self.original_pos = (self.dragged_tile.rect.x, self.dragged_tile.rect.y)
                            return True
                            
                    # Check if a tile on the board was clicked
                    board_tile = self.board.get_tile_at(event.pos[0], event.pos[1])
                    if board_tile and board_tile in self.board.current_turn_tiles:
                        if board_tile.letter == '_':
                            self.blank_tile_selection = board_tile
                            return True
                            
                    # Check if a button was clicked
                    if self.end_turn_button.collidepoint(event.pos):
                        # Calculate score for current turn
                        turn_score = self.scoring.calculate_turn_score(self.board.current_turn_tiles, self.board)
                        bonus = self.scoring.calculate_bonus(len(self.board.current_turn_tiles))
                        total_score = turn_score + bonus
                        
                        # End the turn
                        success, message, placed_tiles_count = self.board.end_turn()
                        if success:
                            # Update player's score
                            self.player_score += total_score
                            
                            # Fill the rack with new tiles
                            for _ in range(placed_tiles_count):
                                tile = self.tile_bag.draw_tile()
                                if tile:
                                    self.tile_rack.add_tile(tile)
                            
                            # Switch to AI's turn
                            self.is_player_turn = False
                            
                            # Update message
                            self.message = f"Turn completed! Score: {turn_score} + {bonus} bonus = {total_score}"
                            self.message_color = (0, 255, 0)
                            
                            # Clear any dragged tiles
                            self.dragged_tile = None
                            self.tile_rack.selected_tile = None
                            
                            # Force a redraw
                            self.draw()
                            pygame.display.flip()
                        else:
                            self.message = message
                            self.message_color = (255, 0, 0)
                        
                        self.message_timer = 60
                        return True
                        
                    if self.replace_button.collidepoint(event.pos):
                        # Replace all tiles in the rack
                        old_tiles = self.tile_rack.tiles.copy()
                        self.tile_rack.tiles.clear()
                        for tile in old_tiles:
                            self.tile_bag.return_tile(tile)
                        # Fill rack with new tiles
                        while len(self.tile_rack.tiles) < 7:
                            tile = self.tile_bag.draw_tile()
                            if tile:
                                self.tile_rack.add_tile(tile)
                        self.is_player_turn = False  # Switch to AI's turn
                        self.message = "Tiles replaced"
                        self.message_color = (0, 255, 0)
                        self.message_timer = 60
                        return True
                        
                    # Check if a letter was selected for blank tile
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
                                
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragged_tile:  # Left click release
                    # Get the grid position for the tile
                    grid_pos = self.board.snap_position(event.pos[0], event.pos[1])
                    
                    if grid_pos and self.board.can_place(*grid_pos):
                        # Try to place the tile on the board
                        if self.board.place_tile(self.dragged_tile, *grid_pos):
                            self.tile_rack.remove_tile(self.dragged_tile)
                            # Check if the placed tile is a blank tile
                            if self.dragged_tile.letter == '_':
                                self.blank_tile_selection = self.dragged_tile
                        else:
                            # Return tile to rack if placement failed
                            self.tile_rack.add_tile(self.dragged_tile)
                            self.tile_rack._update_tile_positions()
                    else:
                        # Return tile to rack if not over a valid position
                        self.tile_rack.add_tile(self.dragged_tile)
                        self.tile_rack._update_tile_positions()
                        
                    self.dragged_tile = None
                    return True
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragged_tile:
                    self.dragged_tile.rect.x = event.pos[0] - self.dragged_tile.rect.width // 2
                    self.dragged_tile.rect.y = event.pos[1] - self.dragged_tile.rect.height // 2
                    return True
                    
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

    def update(self):
        # Update message timer
        if self.message_timer and pygame.time.get_ticks() > self.message_timer:
            self.message = ""
            self.message_timer = 0

    def draw(self):
        """Draw the game state."""
        # Clear the screen
        self.screen.fill(WHITE)
        
        # Draw the board
        self.board.draw(self.screen)
        
        # Draw the tile rack
        self.tile_rack.draw(self.screen)
        
        # Draw the tile bag
        self.tile_bag.draw(self.screen)
        
        # Draw the AI's rack
        self.ai_player.draw(self.screen)
        
        # Draw the end turn button
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.end_turn_button)
        text = self.button_font.render("End Turn", True, WHITE)
        text_rect = text.get_rect(center=self.end_turn_button.center)
        self.screen.blit(text, text_rect)
        
        # Draw the replace button
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.replace_button)
        text = self.button_font.render("Replace", True, WHITE)
        text_rect = text.get_rect(center=self.replace_button.center)
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
                if button['rect'].collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (150, 150, 255), button['rect'], 2)
        
        # Draw scores
        player_score_text = self.message_font.render(f"Your Score: {self.player_score}", True, BLACK)
        self.screen.blit(player_score_text, (10, 10))
        
        # Draw turn indicator
        turn_text = self.message_font.render(
            "Your Turn" if self.is_player_turn else "AI's Turn",
            True,
            SUCCESS_COLOR if self.is_player_turn else ERROR_COLOR
        )
        self.screen.blit(turn_text, (SCREEN_WIDTH // 2 - 50, 10))
        
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
