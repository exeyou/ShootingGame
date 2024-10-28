import pygame
from game_manager import GameManager
from settings import win_width, win_height, background_image, FPS
clock = pygame.time.Clock()
def main():
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))
    game_manager = GameManager(win)

    while True:
        for event in pygame.event.get():
            game_manager.handle_events(event)
        game_manager.update()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
