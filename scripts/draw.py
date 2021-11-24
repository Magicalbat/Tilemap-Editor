import pygame

def drawTilemap(win, drawTiles, tileSize, tileImgs):
    for layer in drawTiles:
        for pStr, imgIndex in layer.items():
            pStr = pStr.split(';')
            tilePos = pygame.math.Vector2((int(pStr[0]), int(pStr[1])))

            win.blit(tileImgs[imgIndex], tilePos * tileSize)