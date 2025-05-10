import pygame
import sys
from board import ScrabbleBoard
from tile import Tile

TILE_SIZE = 40
WIDTH, HEIGHT = TILE_SIZE * 20, TILE_SIZE * 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrabble Board")
clock = pygame.time.Clock()

board = ScrabbleBoard()
tiles = [Tile('A', 100, 100)]  # You can add more tiles if needed

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
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

    board.draw(screen)
    for t in tiles:
        t.draw(screen)

    pygame.display.flip()
    clock.tick(60)
