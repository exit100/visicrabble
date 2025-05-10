import pygame
import sys
from board import ScrabbleBoard
from tile import Tile
from tilebag import TileBag

TILE_SIZE = 40
WIDTH, HEIGHT = TILE_SIZE * 20, TILE_SIZE * 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrabble Board")
clock = pygame.time.Clock()

# Initialize board and tile bag
board = ScrabbleBoard()
tile_bag = TileBag()

# Initialize the tiles on the board (the player takes tiles from the bag)
tiles = []

# The initial position for a new tile drawn from the TileBag
TILEBAG_X = WIDTH - 120 - 10  # X position of the TileBag
TILEBAG_Y = 10  # Y position of the TileBag

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if clicked on the TileBag
                mouse_x, mouse_y = event.pos
                if (TILEBAG_X <= mouse_x <= TILEBAG_X + 120 and TILEBAG_Y <= mouse_y <= TILEBAG_Y + 40):
                    # Only pop a tile if there are remaining tiles
                    if tile_bag.remaining_tiles() > 0:
                        # Draw a new tile from the tile bag
                        drawn_tile = tile_bag.draw_tile()
                        if drawn_tile:
                            tiles.append(drawn_tile)
                            drawn_tile.dragging = True
                            # Place the tile right where the TileBag is
                            drawn_tile.rect.topleft = (TILEBAG_X + 10, TILEBAG_Y + 10)
                            mouse_x, mouse_y = event.pos
                            offset_x = drawn_tile.rect.x - mouse_x
                            offset_y = drawn_tile.rect.y - mouse_y
                            
                # Check if a tile was clicked and start dragging
                for t in tiles:
                    if t.rect.collidepoint(event.pos):
                        t.dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = t.rect.x - mouse_x
                        offset_y = t.rect.y - mouse_y
                        board.remove_tile(t)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for t in tiles:
                    if t.dragging:
                        t.dragging = False
                        snap = board.snap_position(*event.pos)
                        if snap:
                            row, col = snap
                            if board.place_tile(t, row, col):
                                board.print_placed_tiles()
                            else:
                                t.rect.topleft = (100, 100)
                        else:
                            t.rect.topleft = (100, 100)

        elif event.type == pygame.MOUSEMOTION:
            for t in tiles:
                if t.dragging:
                    mouse_x, mouse_y = event.pos
                    t.rect.x = mouse_x + offset_x
                    t.rect.y = mouse_y + offset_y

    # Draw the board and tiles
    board.draw(screen)
    for t in tiles:
        t.draw(screen)

    # Draw the TileBag
    tile_bag.draw(screen)

    pygame.display.flip()
    clock.tick(60)
