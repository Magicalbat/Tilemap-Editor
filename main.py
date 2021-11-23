"""
TODO:
 - Event and action based input system
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

width = 320
height = 180
win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 8)
pygame.display.set_caption("Tilemap Editor")

clock = pygame.time.Clock()
fps = 60

from scripts.input import Input

inp = Input("profile.json")

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
    
    win.fill((200,200,200))

    pygame.display.update()

pygame.quit()