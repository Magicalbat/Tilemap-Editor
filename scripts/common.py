import pygame
import copy

def updateDictionary(d, start, end, reverse=False):
    if reverse:
        tempE = end
        end = start
        start = tempE
    for key in start.keys():
        if isinstance(end[key], type(None)):
            if key in d:    d.pop(key)
        else:
            d[key] = end[key]

def createGrid(width, height, tileSize):
    gridSurf = pygame.Surface((width, height)).convert()
    gridSurf.set_colorkey((0,0,0))
    for x in range(int(width/tileSize) + 1):
        pygame.draw.line(gridSurf, (255,255,255), (x * tileSize, 0), (x * tileSize, height), 1)
        pygame.draw.line(gridSurf, (255,255,255), ((x + 1) * tileSize - 1, 0), ((x + 1) * tileSize - 1, height), 1)
    for y in range(int(height/tileSize) + 1):
        pygame.draw.line(gridSurf, (255,255,255), (0, y * tileSize), (width, y * tileSize), 1)
        pygame.draw.line(gridSurf, (255,255,255), (0, (y + 1) * tileSize - 1), (width, (y + 1) * tileSize - 1), 1)
    
    gridSurf.set_alpha(64)
    
    return gridSurf.copy()

def loadSpriteSheet(imgPath, spriteSize, dim, padding, count, colorKey=None):
    mainImg = pygame.image.load(imgPath).convert()

    if colorKey is not None:
        mainImg.set_colorkey(colorKey, pygame.RLEACCEL)
    
    imgs = []

    i = 0
    for y in range(dim[1]):
        for x in range(dim[0]):
            rect = pygame.Rect(x * (spriteSize[0] + padding[0]), y * (spriteSize[0] + padding[1]), spriteSize[0], spriteSize[1])
            
            rect.right = min(rect.right, mainImg.get_width())
            rect.bottom = min(rect.bottom, mainImg.get_height())

            imgs.append(mainImg.subsurface(rect))

            i += 1

            if i > count - 1:
                return imgs
    
    return imgs

def swapImgColor(img, oldCol, newCol):
    outImg = pygame.Surface((img.get_width(), img.get_height()))
    outImg.fill(newCol)

    imgCopy = img.copy()
    imgCopy.set_colorkey(oldCol)

    outImg.blit(imgCopy, (0,0))

    outImg.set_colorkey(img.get_colorkey())
    
    return outImg

def setCursorFromTxt(filePath):
    lines = None
    with open(filePath, 'r') as f:
        lines = f.read().split('\n')
    
    hotspot = [0,0]

    if ';' in lines[0]:
        pStr = lines[0].split(';')
        hotspot = [int(pStr[0]), int(pStr[1])]
        lines.pop(0)

    xormasks, andmasks = pygame.cursors.compile(lines)
    pygame.mouse.set_cursor((len(lines), len(lines[0])), hotspot, xormasks, andmasks)

def setCursorFromImg(imgPath, hotspotChar="X", txtFilePath=""):
    img = pygame.image.load(imgPath).convert_alpha()

    hotspot = []
    lines = []
    for y in range(img.get_height()):
        line = ""
        for x in range(img.get_width()):
            if img.get_at((x, y)) == (0,0,0):
                line += "X"
            elif img.get_at((x, y)) == (255,255,255):
                line += "."
            elif img.get_at((x, y)) == (255,0,0):
                hotspot = [x, y]
                line += hotspotChar
            else:
                line += " "
        lines.append(line)

    if txtFilePath != "":
        with open(txtFilePath, 'w') as f:
            f.write(f"{hotspot[0]};{hotspot[1]}\n")
            for i in range(len(lines)):
                if i == len(lines) - 1:
                    f.write(lines[i])
                else:
                    f.write(lines[i] + '\n')

    
    xormasks, andmasks = pygame.cursors.compile(lines)
    pygame.mouse.set_cursor((len(lines), len(lines[0])), hotspot, xormasks, andmasks)
