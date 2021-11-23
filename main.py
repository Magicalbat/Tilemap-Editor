"""
TODO:
 - Tilesets
 - Auto tiling
 - Tileset editor
 - Tools (pencil, box select, bucket, color picker)
 - Undos and Redos
 - Middlemouse scrolling
 - Saving and save box when closing
 - Export settings
 - Personalization settings (Ex: custom keybinds)
"""

import pygame
import time

pygame.init()

width = int(320 * 1.5)
height = int(180 * 1.5)
win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 8)
pygame.display.set_caption("Tilemap Editor")

clock = pygame.time.Clock()
fps = 60

from scripts.input import Input
from scripts.common import *

inp = Input("profile.json")

cellSize = 8

# GRID
gridVisible = False
gridSurf = createGrid(width + 2 * cellSize, height + 2 * cellSize, cellSize)

running = True
while running:
    clock.tick(fps)
    
    inp.passiveUpdate()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            inp.eventUpdate(event.key, True)
        if event.type == pygame.KEYUP:
            inp.eventUpdate(event.key, False)
    
    if inp.isActionJustPressed("Grid"):
        gridVisible = not gridVisible

    win.fill((150,150,150))
    
    if gridVisible:
        win.blit(gridSurf, (-cellSize, -cellSize))

    pygame.display.update()

pygame.quit()