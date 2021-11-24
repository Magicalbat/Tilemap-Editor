import pygame

def createGrid(width, height, tileSize):
    gridSurf = pygame.Surface((width, height)).convert()
    gridSurf.set_colorkey((0,0,0))
    for x in range(int(width/tileSize) + 1):
        pygame.draw.line(gridSurf, (255,255,255), (x * tileSize, 0), (x * tileSize, height), 1)
    for y in range(int(height/tileSize) + 1):
        pygame.draw.line(gridSurf, (255,255,255), (0, y * tileSize), (width, y * tileSize), 1)
    
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