from objects import Player, Block, Enemy, InputHandler, GameManager
from settings import *
import pygame
import random

pygame.init()
win = pygame.display.set_mode((win_width, win_height))
clock = pygame.time.Clock()

game_manager = GameManager(win)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if not game_manager.is_running() and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_manager.start_game()

    game_manager.update()
    pygame.display.update()
    clock.tick(FPS)
