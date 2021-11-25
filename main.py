"""
TODO:
 - Tilesets
 - Auto tiling
 - Tileset editor
 - Tools (pencil, box select, bucket, color picker)
 - Middlemouse scrolling
 - Saving and save box when closing
 - Export settings
 - Personalization settings (Ex: custom keybinds)
"""

import pygame
from pygame.display import update

pygame.init()

width = int(320 * 1.5)
height = int(180 * 1.5)
win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 8)
pygame.display.set_caption("Tilemap Editor")

clock = pygame.time.Clock()
fps = 60

import json, copy

data = ""
with open("profile.json", 'r') as f:
    data = f.read()
profile = json.loads(data)

from scripts.input import Input
from scripts.text import Text
from scripts.common import *

inp = Input()
inp.loadWithDictionary(profile["input"])

text = Text()
text.loadFontImg("res/text.png", scale=(2,2))

# TILES
tileSize = 12
tileImgs = loadSpriteSheet("res/tiles.png", (12,12), (4,4), (1,1), 16, (0,0,0))
currentTile = 0

# TILEMAP
layers = 1
currentLayer = 0
drawTiles = [{} for _ in range(layers)]

# UNDO / REDO
changeHistory = []
currentChangeLog = [[{}, {}] for _ in range(layers)]
undoing = False
undoIndex = 0

# GRID
gridVisible = False
gridSurf = createGrid(width + 2 * tileSize, height + 2 * tileSize, tileSize)

# CURSOR INIT
#setCursorFromTxt("res/levelEditor/pencil.txt")
setCursorFromImg("res/levelEditor/grab hand.png", ".", "res/levelEditor/grab hand.txt")

# SIDEBAR and MAIN SURFACE
sideBarFraction = 0.2
sideBarDim = (int(width * sideBarFraction), height)
sideBar = pygame.Surface(sideBarDim).convert()
sideBar.set_colorkey((0,0,0))
sideBarCol = profile["colors"]["Side Bar"]

tileViewDim = (int(width * (1 - sideBarFraction)), height)
tileViewPos = pygame.math.Vector2((int(width * sideBarFraction), 0))
tileView = pygame.Surface(tileViewDim).convert()
tileView.set_colorkey((0,0,0))
tileViewCol = profile["colors"]["Tileview"]

tilePreviewSurf = pygame.Surface((tileSize, tileSize)).convert()
tilePreviewSurf.fill((0,255,0))
tilePreviewSurf.set_alpha(64)

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

    mousePos = pygame.math.Vector2(pygame.mouse.get_pos())
    tvMousePos = pygame.math.Vector2((mousePos.x - tileViewPos.x, mousePos.y)) # Tile View Mouse Pos
    tileMousePos = pygame.math.Vector2((int(tvMousePos.x / tileSize), int(tvMousePos.y / tileSize)))
    clampedMousePos = tileMousePos * tileSize
    
    mousePosStr = f"{int(tileMousePos.x)};{int(tileMousePos.y)}"
    
    if inp.isMouseButtonJustReleased(0):
        changeHistory.append(copy.deepcopy(currentChangeLog))
        currentChangeLog = [[{}, {}] for _ in range(len(drawTiles))]
        if len(changeHistory) > 10:
            changeHistory = changeHistory[-10:]
    
    if inp.isActionJustPressed("Undo"):
        if not undoing:
            undoing = True
            undoIndex = len(changeHistory) 

        if undoing:
            undoIndex -= 1
            undoIndex = max(0, undoIndex)
            if undoIndex >= 0:
                for i in range(len(drawTiles)):
                    updateDictionary(drawTiles[i], changeHistory[undoIndex][currentLayer][0], changeHistory[undoIndex][currentLayer][1], True)
    
    if undoing and inp.isActionJustPressed("Redo"):
        undoIndex = min(len(changeHistory) - 1, undoIndex)
        if undoIndex >= 0:
            for i in range(len(drawTiles)):
                updateDictionary(drawTiles[i], changeHistory[undoIndex][currentLayer][0], changeHistory[undoIndex][currentLayer][1], False)
        undoIndex += 1

    if inp.isMouseButtonPressed(0):
        if undoing:
            undoing = False
            changeHistory = changeHistory[:undoIndex]
        
        if mousePosStr not in drawTiles[currentLayer]:
            currentChangeLog[currentLayer][0][mousePosStr] = drawTiles[currentLayer][mousePosStr] if mousePosStr in drawTiles[currentLayer] else None
            drawTiles[currentLayer][mousePosStr] = currentTile
            currentChangeLog[currentLayer][1][mousePosStr] = currentTile
        
    # TILE VIEW DRAW
    if inp.isActionJustPressed("Grid"):
        gridVisible = not gridVisible

    tileView.fill(tileViewCol)
    
    if gridVisible:
        tileView.blit(gridSurf, (-tileSize, -tileSize))
    
    for layer in drawTiles:
        for pStr, imgIndex in layer.items():
            pStr = pStr.split(';')
            tilePos = pygame.math.Vector2((int(pStr[0]), int(pStr[1])))
        
            tileView.blit(tileImgs[imgIndex], tilePos * tileSize)
    
    #if mousePosStr not in drawTiles[currentLayer]:
    tileView.blit(tilePreviewSurf, clampedMousePos)
    
    # SIDEBAR DRAW
    sideBar.fill(sideBarCol)

    sideBar.blit(text.createTextSurf(f"({tileMousePos.x},{tileMousePos.y})"), (0,0))

    if undoing:
        pygame.draw.rect(sideBar, (0,0,255), (5, 25, 25, 25))
    
    win.blit(tileView, tileViewPos)
    win.blit(sideBar, (0,0))
    pygame.display.update()

pygame.quit()