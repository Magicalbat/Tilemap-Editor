import pygame

def createGrid(width, height, cellSize):
    gridSurf = pygame.Surface((width, height)).convert()
    gridSurf.set_colorkey((0,0,0))
    for x in range(int(width/cellSize) + 1):
        pygame.draw.line(gridSurf, (255,255,255), (x * cellSize, 0), (x * cellSize, height), 1)
    for y in range(int(height/cellSize) + 1):
        pygame.draw.line(gridSurf, (255,255,255), (0, y * cellSize), (width, y * cellSize), 1)
    
    gridSurf.set_alpha(64)
    
    return gridSurf.copy()