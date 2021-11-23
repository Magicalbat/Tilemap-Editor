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

# SIDEBAR and MAIN SURFACE
sideBarFraction = 0.2
sideBarDim = (int(width * sideBarFraction), height)
sideBar = pygame.Surface(sideBarDim).convert()
sideBar.set_colorkey((0,0,0))

tileViewDim = (int(width * (1 - sideBarFraction)), height)
tileViewPos = pygame.math.Vector2((int(width * sideBarFraction), 0))
tileView = pygame.Surface(tileViewDim).convert()
tileView.set_colorkey()

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

    tileView.fill((150,150,150))
    
    if gridVisible:
        tileView.blit(gridSurf, (-cellSize, -cellSize))
    
    win.blit(tileView, tileViewPos)
    win.blit(sideBar, (0,0))
    pygame.display.update()

pygame.quit()