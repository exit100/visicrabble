import pygame

TILE_SIZE = 40
TILE_COLOR = (173, 216, 230)
TEXT_COLOR = (0, 0, 0)

pygame.font.init()
font = pygame.font.SysFont(None, 40)

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
