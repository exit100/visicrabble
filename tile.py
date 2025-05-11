import pygame

TILE_SIZE = 45  # Slightly larger tiles
TILE_COLOR = (255, 248, 220)  # Cream color
TILE_BORDER = (139, 69, 19)  # Brown border
TEXT_COLOR = (0, 0, 0)
TILE_RADIUS = 8  # Radius for rounded corners

pygame.font.init()
font = pygame.font.SysFont('Arial', 32, bold=True)
score_font = pygame.font.SysFont('Arial', 16)

class Tile:
    def __init__(self, letter, x, y, score):
        self.letter = letter
        self.score = score
        self.chosen_letter = None  # For blank tiles
        self.is_blank = letter == '_'  # Track if this is a blank tile

        # Create a surface with per-pixel alpha
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.update_display()

        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.placed_cell = None
        self.in_rack = True  # Track if tile is in the rack

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def place(self, row, col):
        self.placed_cell = (row, col)
        self.in_rack = False

    def unplace(self):
        self.placed_cell = None
        self.in_rack = True

    def update_display(self):
        # Recreate the tile image with updated letter
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Draw rounded rectangle background
        pygame.draw.rect(self.image, TILE_COLOR, (0, 0, TILE_SIZE, TILE_SIZE), border_radius=TILE_RADIUS)
        pygame.draw.rect(self.image, TILE_BORDER, (0, 0, TILE_SIZE, TILE_SIZE), width=2, border_radius=TILE_RADIUS)

        # Draw letter
        if self.is_blank:
            display_letter = self.chosen_letter if self.chosen_letter else '_'
            text_color = (100, 100, 100)  # Gray color for blank tiles
        else:
            display_letter = self.letter
            text_color = TEXT_COLOR

        text = font.render(display_letter, True, text_color)
        text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2 - 2))
        self.image.blit(text, text_rect)

        # Draw score (bottom-right)
        score_text = score_font.render(str(self.score), True, TEXT_COLOR)
        score_rect = score_text.get_rect(bottomright=(TILE_SIZE - 5, TILE_SIZE - 5))
        self.image.blit(score_text, score_rect)
