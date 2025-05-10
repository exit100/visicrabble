import pygame
from tile import Tile
import random

TILEBAG_WIDTH, TILEBAG_HEIGHT = 120, 40
TILEBAG_MARGIN = 10

class TileBag:
    def __init__(self):
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tile_data = [
            ('A', 1, 9), ('B', 3, 2), ('C', 3, 2), ('D', 2, 4), ('E', 1, 12),
            ('F', 4, 2), ('G', 2, 3), ('H', 4, 2), ('I', 1, 9), ('J', 8, 1),
            ('K', 5, 1), ('L', 1, 4), ('M', 3, 2), ('N', 1, 6), ('O', 1, 8),
            ('P', 3, 2), ('Q', 10, 1), ('R', 1, 6), ('S', 1, 4), ('T', 1, 6),
            ('U', 1, 4), ('V', 4, 2), ('W', 4, 2), ('X', 8, 1), ('Y', 4, 2),
            ('Z', 10, 1), ('_', 0, 2)
        ]
        
        tiles = []
        for letter, score, count in tile_data:
            for _ in range(count):
                tiles.append(Tile(letter, 0, 0, score))

        random.shuffle(tiles)
        print(f"Initialized tile bag with {len(tiles)} tiles")
        return tiles

    def draw(self, surface):
        # Draw the TileBag representation at the top-right corner
        pygame.draw.rect(surface, (0, 0, 0), (surface.get_width() - TILEBAG_WIDTH - TILEBAG_MARGIN, TILEBAG_MARGIN, TILEBAG_WIDTH, TILEBAG_HEIGHT))
        pygame.draw.rect(surface, (255, 255, 255), (surface.get_width() - TILEBAG_WIDTH - TILEBAG_MARGIN + 2, TILEBAG_MARGIN + 2, TILEBAG_WIDTH - 4, TILEBAG_HEIGHT - 4))  # Inner color
        
        # Display the number of remaining tiles in the bag
        font = pygame.font.SysFont(None, 30)
        remaining_text = font.render(f"Tiles: {self.remaining_tiles()}", True, (0, 0, 0))
        surface.blit(remaining_text, (surface.get_width() - TILEBAG_WIDTH - TILEBAG_MARGIN + 10, TILEBAG_MARGIN + 10))

    def draw_tile(self):
        if self.tiles:
            tile = self.tiles.pop()
            print(f"Drew tile {tile.letter} from bag. {len(self.tiles)} tiles remaining")
            return tile
        else:
            print("No tiles left in bag")
            return None

    def remaining_tiles(self):
        return len(self.tiles)
