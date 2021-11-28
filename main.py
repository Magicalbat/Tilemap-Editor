"""
TODO:
 - Tilesets
 - Auto tiling
 - Tileset editor
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

import json, copy, sys, os, math
from dataclasses import dataclass, InitVar
from typing import List, ClassVar
from easygui import buttonbox

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
def loadMap(filePath):
    global drawTiles, layers
    if os.path.exists(filePath):
        loadedMap = {}
        with open(filePath, 'r') as f:   loadedMap = json.loads(f.read())
        drawTiles = loadedMap["drawTiles"]
        layers = len(drawTiles)
    else:
        print(f"Could not open file at \"{filePath}\".")

if profile["load map"]:    loadMap(profile["load map"])
elif len(sys.argv) > 1:    loadMap(sys.argv[1])

def getSaveData():
    return {
        "drawTiles" : drawTiles
    }

currentSavedData = copy.deepcopy(getSaveData())

def saveMap(filePath="output.json"):
    global currentSavedData
    currentSavedData = copy.deepcopy(getSaveData())
    output = currentSavedData

    with open(filePath, 'w') as f:
        if profile["export"]["indent"]:
            f.write(json.dumps(output, indent=profile["export"]["indent"]))
        else:
            f.write(json.dumps(output))

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

@dataclass
class TileSelection:
    dim : tuple
    col : tuple
    pos : pygame.Vector2
    indent : int
    scrollSpeed : int
    scrollDir : int
    imgs : InitVar[list]
    tileSize : InitVar[int]
    rect : ClassVar[pygame.Rect]
    surf : ClassVar[pygame.Surface]
    rects : ClassVar[List[pygame.Rect]]
    num : int = 3
    scroll : int = 0

    def __post_init__(self, imgs, tileSize):
        self.rect = pygame.Rect((self.pos.x, self.pos.y, self.dim[0], self.dim[1]))
        self.surf = pygame.Surface(self.dim).convert()
        self.surf.set_colorkey((0,0,0))
        self.rects = []
        for i, img in enumerate(imgs):
            pos = (
                self.indent + (tileSize * 2 * (i % self.num)),\
                self.indent + (tileSize * 2 * (i // self.num))\
            )
            self.surf.blit(img, pos)
            self.rects.append([pos[0] + self.pos[0], pos[1] + self.pos[1], tileSize, tileSize])

tempDim = (int(sideBarDim[0] * 0.8), int(sideBarDim[1] * 0.6))
ts = TileSelection(
    tempDim, (max(0, sideBarCol[0] - 15), max(0, sideBarCol[1] - 15), max(0, sideBarCol[2] - 15)),\
    pygame.math.Vector2((int((sideBarDim[0] - tempDim[0]) / 2), 42)), tileSize / 2, profile["scroll speed"],\
    -1 + profile["reverse scroll"] * 2, tileImgs, tileSize\
)
del tempDim

#tselectionDim = (int(sideBarDim[0] * 0.8), int(sideBarDim[1] * 0.6))
#tselectionSurf = pygame.Surface(tselectionDim).convert()
#tselectionSurf.set_colorkey((0,0,0))
#tselectionCol = (max(0, sideBarCol[0] - 15), max(0, sideBarCol[1] - 15), max(0, sideBarCol[2] - 15))
#tselectionPos = (int((sideBarDim[0] - tselectionDim[0]) / 2), 42)
#tselectionRect = pygame.Rect((tselectionPos[0], tselectionPos[1], tselectionDim[0], tselectionDim[1]))
#
#tselectionIndent = int(tileSize / 2)
#tselectionNum = 3
#
#tselectionRects = []
#for i, img in enumerate(tileImgs):
#    pos = (
#        tselectionIndent + (tileSize * 2 * (i % tselectionNum)),\
#        tselectionIndent + (tileSize * 2 * (i // tselectionNum))\
#    )
#    tselectionSurf.blit(img, pos)
#    tselectionRects.append([pos[0] + tselectionPos[0], pos[1] + tselectionPos[1], tileSize, tileSize])
#
#tselectionScroll = 0
#tselectionScrollSpeed = profile["scroll speed"]
#tselectionScrollDir = -1 + profile["reverse scroll"] * 2

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
    
    mousePos = pygame.math.Vector2(pygame.mouse.get_pos())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if getSaveData() != currentSavedData:
                choice = buttonbox("", "Save changes before closing?", ("Save", "Do not save", "Cancel"), default_choice="Save", cancel_choice="Cancel")
                if choice == "Save":
                    saveMap()
                if choice != "Cancel":
                    running = False
            else:
                running = False
        if event.type == pygame.KEYDOWN:
            inp.eventUpdate(event.key, True)
        if event.type == pygame.KEYUP:
            inp.eventUpdate(event.key, False)
        if event.type == pygame.MOUSEWHEEL:
            if mousePos.x < tileViewPos.x:
                scrollAmount = ts.scrollSpeed * delta * event.y * ts.scrollDir
                ts.scroll += scrollAmount
                for r in ts.rects:
                    r[1] -= scrollAmount
    
    if inp.isActionJustPressed("Save") and inp.isActionPressed("Control"):
        saveMap()
    
    if editState != EditStates.SCROLL_GRAB:
        if inp.isActionJustPressed("Pencil"):   changeState(EditStates.PENCIL)
        if inp.isActionJustPressed("Box Select") and inp.isActionReleased("Control"):   changeState(EditStates.BOX_SELECT)
        if inp.isActionJustPressed("Bucket"):   changeState(EditStates.BUCKET)
        if inp.isActionJustPressed("Color Picker"):   changeState(EditStates.COLOR_PICKER)

    tvMousePos = pygame.math.Vector2((mousePos.x - tileViewPos.x, mousePos.y)) # Tile View Mouse Pos
    tvMousePos += scroll
    tileMousePos = pygame.math.Vector2((math.floor(tvMousePos.x / tileSize), math.floor(tvMousePos.y / tileSize)))
    
    mousePosStr = f"{int(tileMousePos.x)};{int(tileMousePos.y)}"

    if mousePos.x < tileViewPos.x:
        if inp.isMouseButtonJustPressed(0):
            for i, r in enumerate(ts.rects):
                rect = pygame.Rect(r)
                if rect.collidepoint(mousePos):
                    currentTile = i
    else:
        if inp.isMouseButtonJustPressed(1) or inp.isActionJustPressed("Alt Scroll Grab"):
            startScrollDrag = tvMousePos
            prevState = editState
            changeState(EditStates.SCROLL_GRAB)
        if inp.isMouseButtonPressed(1) or inp.isActionPressed("Alt Scroll Grab"):
            scroll += startScrollDrag - tvMousePos
        if inp.isMouseButtonJustReleased(1) or inp.isActionJustReleased("Alt Scroll Grab"):
            changeState(prevState)
            prevState = EditStates.NONE

        if inp.isMouseButtonJustReleased(0) or inp.isMouseButtonJustReleased(2):
            changeHistory.append(copy.deepcopy(currentChangeLog))
            currentChangeLog = [[{}, {}] for _ in range(len(drawTiles))]
            if len(changeHistory) > 10:
                changeHistory = changeHistory[-10:]

        if inp.isActionJustPressed("Undo") and inp.isActionPressed("Control"):
            if not undoing:
                undoing = True
                undoIndex = len(changeHistory) 

            if undoing:
                undoIndex -= 1
                undoIndex = max(0, undoIndex)
                if undoIndex >= 0:
                    for i in range(len(drawTiles)):
                        updateDictionary(drawTiles[i], changeHistory[undoIndex][currentLayer][0], changeHistory[undoIndex][currentLayer][1], True)

        if undoing and inp.isActionJustPressed("Undo") and inp.isActionPressed("Control") and inp.isActionPressed("Shift"):
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
    
    if editState != EditStates.BOX_SELECT and prevState != EditStates.BOX_SELECT:  tileView.blit(tilePreviewSurf, (tileMousePos * tileSize) - scroll)
    else:
        r = getSelectionTileRect()
        pygame.draw.rect(tileView, (255,255,255), (r.x * tileSize - scroll.x, r.y * tileSize - scroll.y, r.w * tileSize, r.h * tileSize), width=1)
    
    # SIDEBAR DRAW
    sideBar.fill(sideBarCol)

    pygame.draw.rect(sideBar, ts.col, ts.rect)
    sideBar.blit(ts.surf, (ts.pos[0], ts.pos[1] - ts.scroll))
    stRect = ts.rects[currentTile] # Selected tile rect
    pygame.draw.rect(sideBar, (0,255,255), (stRect[0] - 1, stRect[1] - 1, stRect[2] + 1, stRect[3] + 1), width=1)

    #for r in tselectionRects:
    #    pygame.draw.rect(sideBar, (0,255,0), r)
    pygame.draw.rect(sideBar, sideBarCol, (0, 0, sideBarDim[0], ts.rect.y))
    pygame.draw.rect(sideBar, sideBarCol, (0, ts.rect.bottom, sideBarDim[0], sideBarDim[1] - ts.rect.bottom))

    sideBar.blit(text.createTextSurf(f"({tileMousePos.x},{tileMousePos.y})"), (2, 2))
    sideBar.blit(tileImgs[currentTile], (2, 18))

    win.blit(tileView, tileViewPos)
    win.blit(sideBar, (0,0))
    pygame.display.update()

pygame.quit()