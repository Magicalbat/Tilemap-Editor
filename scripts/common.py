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