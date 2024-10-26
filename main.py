from objects import InputHandler, GameManager, Button
from settings import *
import pygame
import random

pygame.init()
win = pygame.display.set_mode((win_width, win_height))
clock = pygame.time.Clock()

game_manager = GameManager(win)

while True:
    for event in pygame.event.get():
        game_manager.handle_events(event)

    game_manager.update()
    pygame.display.update()
    clock.tick(FPS)
