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

def tryResetUndo():
    global undoing, changeHistory, undoIndex
    if undoing:
        undoing = False
        changeHistory = changeHistory[:undoIndex]

# SCROLL
scroll = pygame.math.Vector2((0,0))
startScrollDrag = pygame.math.Vector2((0,0))
prevState = None

# GRID
gridVisible = False
gridSurf = createGrid(width + 2 * tileSize, height + 2 * tileSize, tileSize)

# BOX SELECT
startSelectionPos = endSelectionPos = pygame.math.Vector2((0,0))

def getSelectionTileRect():
    tileRect = pygame.Rect((0,0,0,0))
        
    if startSelectionPos.x < endSelectionPos.x:
        tileRect.x = startSelectionPos.x
        tileRect.w = endSelectionPos.x - startSelectionPos.x + 1
    else:
        tileRect.x = endSelectionPos.x
        tileRect.w = startSelectionPos.x - endSelectionPos.x + 1
    
    if startSelectionPos.y < endSelectionPos.y:
        tileRect.y = startSelectionPos.y
        tileRect.h = endSelectionPos.y - startSelectionPos.y + 1
    else:
        tileRect.y = endSelectionPos.y
        tileRect.h = startSelectionPos.y - endSelectionPos.y + 1
    
    return tileRect

# CURSOR INIT
editState = EditStates.PENCIL
changeCursorFromState(editState)
def changeState(state):
    global editState
    editState = state
    changeCursorFromState(editState)

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
    delta = clock.get_time() / 1000
    
    inp.passiveUpdate()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            inp.eventUpdate(event.key, True)
        if event.type == pygame.KEYUP:
            inp.eventUpdate(event.key, False)
    
    if inp.isActionJustPressed("Extra Data"):   currentTile += 1
    
    if editState != EditStates.SCROLL_GRAB:
        if inp.isActionJustPressed("Pencil"):   changeState(EditStates.PENCIL)
        if inp.isActionJustPressed("Box Select"):   changeState(EditStates.BOX_SELECT)
        if inp.isActionJustPressed("Bucket"):   changeState(EditStates.BUCKET)
        if inp.isActionJustPressed("Color Picker"):   changeState(EditStates.COLOR_PICKER)

    mousePos = pygame.math.Vector2(pygame.mouse.get_pos())
    tvMousePos = pygame.math.Vector2((mousePos.x - tileViewPos.x, mousePos.y)) # Tile View Mouse Pos
    tvMousePos += scroll
    tileMousePos = pygame.math.Vector2((int(tvMousePos.x / tileSize), int(tvMousePos.y / tileSize)))
    if tileMousePos.x < 0:  tileMousePos.x -= 1
    if tileMousePos.y < 0:  tileMousePos.y -= 1
    
    mousePosStr = f"{int(tileMousePos.x)};{int(tileMousePos.y)}"

    if inp.isMouseButtonJustPressed(1) or inp.isActionJustPressed("Alt Scroll Grab"):
        startScrollDrag = tvMousePos
        prevState = editState
        changeState(EditStates.SCROLL_GRAB)
    if inp.isMouseButtonPressed(1) or inp.isActionPressed("Alt Scroll Grab"):
        scroll += startScrollDrag - tvMousePos
    if inp.isMouseButtonJustReleased(1) or inp.isActionJustReleased("Alt Scroll Grab"):    changeState(prevState)

    if inp.isMouseButtonJustReleased(0) or inp.isMouseButtonJustReleased(2):
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

    if inp.isMouseButtonPressed(2):
        tryResetUndo()
        
        if editState == EditStates.PENCIL:
            if mousePosStr in drawTiles[currentLayer]:
                currentChangeLog[currentLayer][0][mousePosStr] = drawTiles[currentLayer][mousePosStr]
                drawTiles[currentLayer].pop(mousePosStr)
                currentChangeLog[currentLayer][1][mousePosStr] = None


    if inp.isMouseButtonJustPressed(0):
        tryResetUndo()
        
        if editState == EditStates.COLOR_PICKER:
            if mousePosStr in drawTiles[currentLayer]:
                currentTile = drawTiles[currentLayer][mousePosStr]
                changeState(EditStates.PENCIL)
        elif editState == EditStates.BOX_SELECT:
            startSelectionPos = tileMousePos
        elif editState == EditStates.BUCKET: # BUCKET FILL
            startPos = (tileMousePos.x, tileMousePos.y)
            queue = [startPos]

            while queue:
                curPos = queue.pop()
                if abs(curPos[0] - startPos[0]) > 20 or abs(curPos[1] - startPos[1]) > 20:  continue

                pStr = f"{int(curPos[0])};{int(curPos[1])}"
                if pStr in drawTiles[currentLayer]: continue
                
                currentChangeLog[currentLayer][0][pStr] = None
                drawTiles[currentLayer][pStr] = currentTile
                currentChangeLog[currentLayer][1][pStr] = currentTile

                queue.insert(0, (curPos[0] + 1, curPos[1]))
                queue.insert(0, (curPos[0] - 1, curPos[1]))
                queue.insert(0, (curPos[0], curPos[1] + 1))
                queue.insert(0, (curPos[0], curPos[1] - 1))
    
    if inp.isMouseButtonPressed(0):
        tryResetUndo()
        
        if editState == EditStates.PENCIL:
            if mousePosStr not in currentChangeLog[currentLayer][0]:
                currentChangeLog[currentLayer][0][mousePosStr] = drawTiles[currentLayer][mousePosStr] if mousePosStr in drawTiles[currentLayer] else None
            drawTiles[currentLayer][mousePosStr] = currentTile
            currentChangeLog[currentLayer][1][mousePosStr] = currentTile
        if editState == EditStates.BOX_SELECT:
            endSelectionPos = tileMousePos
    
    if editState == EditStates.BOX_SELECT:
        if inp.isActionJustPressed("Selection Delete"):
            sRect = getSelectionTileRect()
            for x in range(sRect.w):
                for y in range(sRect.h):
                   pStr = f"{int(sRect.x + x)};{int(sRect.y + y)}"
                   if pStr in drawTiles[currentLayer]:
                       currentChangeLog[currentLayer][0][pStr] = drawTiles[currentLayer][pStr]
                       drawTiles[currentLayer].pop(pStr)
                       currentChangeLog[currentLayer][1][pStr] = None
        elif inp.isActionJustPressed("Selection Fill"):
            sRect = getSelectionTileRect()
            for x in range(sRect.w):
                for y in range(sRect.h):
                    pStr = f"{int(sRect.x + x)};{int(sRect.y + y)}"
                    currentChangeLog[currentLayer][0][pStr] = drawTiles[currentLayer][pStr] if pStr in drawTiles[currentLayer] else None
                    drawTiles[currentLayer][pStr] = currentTile
                    currentChangeLog[currentLayer][1][pStr] = currentTile
    
    # TILE VIEW DRAW
    if inp.isActionJustPressed("Grid"):
        gridVisible = not gridVisible

    tileView.fill(tileViewCol)
    
    if gridVisible:
        #pos = (-scroll.x % tileSize, -scroll.y % tileSize)
        tileView.blit(gridSurf, pygame.math.Vector2((-scroll.x % tileSize - tileSize, -scroll.y % tileSize - tileSize)))
    
    for layer in drawTiles:
        for pStr, imgIndex in layer.items():
            pStr = pStr.split(';')
            tilePos = pygame.math.Vector2((int(pStr[0]), int(pStr[1])))
        
            tileView.blit(tileImgs[imgIndex], tilePos * tileSize - scroll)
    
    if editState != EditStates.BOX_SELECT:  tileView.blit(tilePreviewSurf, (tileMousePos * tileSize) - scroll)
    else:
        r = getSelectionTileRect()
        pygame.draw.rect(tileView, (255,255,255), (r.x * tileSize, r.y * tileSize, r.w * tileSize, r.h * tileSize), width=1)
    
    # SIDEBAR DRAW
    sideBar.fill(sideBarCol)

    sideBar.blit(text.createTextSurf(f"({tileMousePos.x},{tileMousePos.y})"), (0,0))

    win.blit(tileView, tileViewPos)
    win.blit(sideBar, (0,0))
    pygame.display.update()

pygame.quit()