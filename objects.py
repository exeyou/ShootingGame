from abc import ABC, abstractmethod
import pygame
from settings import *
import random
import math
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Drawable(ABC):
    @abstractmethod
    def draw(self, win):
        pass

class Movable(ABC):
    @abstractmethod
    def move(self, *args):
        pass

class GameSprite(pygame.sprite.Sprite, Drawable):
    def __init__(self, image, x, y, w, h):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(image), (w, h))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, win):
        win.blit(self.image, self.rect)

class Player(GameSprite, Movable):
    def __init__(self, image, x, y, w, h, speed):
        super().__init__(image, x, y, w, h)
        self.speed = speed
        self.hp = 100
        logging.info("Гравець створений на позиції (%d, %d)", x, y)

    def move(self, keys):
        old_position = self.rect.topleft
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed

        if self.rect.topleft != old_position:
            logging.info("Гравець перемістився на позицію %s", self.rect.topleft)

    def update(self, input_handler, blocks, collision_handler):
        self.move(input_handler.get_keys())
        collision_handler.check_collision(self, blocks)

class Enemy(GameSprite, Movable):
    def __init__(self, image, x, y, w, h, speed):
        super().__init__(image, x, y, w, h)
        self.speed = speed
        logging.info("Ворог створений на позиції (%d, %d)", x, y)

    def move(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

    def update(self, player):
        self.move(player)

    def on_collision(self, player):
        player.hp -= 10
        logging.info("Гравець втратив 10 HP. Залишилося %d HP", player.hp)
        self.kill()

class Block(GameSprite):
    pass

class CollisionHandler:
    @staticmethod
    def check_collision(movable, blocks):
        for block in blocks:
            if movable.rect.colliderect(block.rect):
                logging.info("Зіткнення з блоком на позиції %s", block.rect.topleft)
                CollisionHandler.resolve_collision(movable, block)

    @staticmethod
    def resolve_collision(movable, block):
        if movable.rect.right > block.rect.left and movable.rect.left < block.rect.left:
            movable.rect.right = block.rect.left
        elif movable.rect.left < block.rect.right and movable.rect.right > block.rect.right:
            movable.rect.left = block.rect.right
        elif movable.rect.bottom > block.rect.top and movable.rect.top < block.rect.top:
            movable.rect.bottom = block.rect.top
        elif movable.rect.top < block.rect.bottom and movable.rect.bottom > block.rect.bottom:
            movable.rect.top = block.rect.bottom

class InputHandler:
    def get_keys(self):
        return pygame.key.get_pressed()

class GameManager:
    def __init__(self, win):
        self.win = win
        self.game = False
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = None
        self.scores = 0
        self.collision_handler = CollisionHandler()

    def start_game(self):
        self.game = True
        self.scores = 0
        logging.info("Гра розпочата")
        self._create_objects()

    def _create_objects(self):
        self.player = Player(player_image, 350, 250, 50, 50, 5)

        self.blocks.empty()
        for i in range(3):
            block = Block(block_image, 100 + i * 200, 300, 100, 50)
            self.blocks.add(block)
            logging.info("Блок створений на позиції (%d, %d)", 100 + i * 200, 300)

        self.enemies.empty()
        for _ in range(5):
            enemy = Enemy(zombie_images[0], random.randint(50, 750), random.randint(50, 550), 50, 50, 2)
            self.enemies.add(enemy)

    def update(self):
        if self.game:
            self._run_game()
        else:
            self._display_start_message()

    def _run_game(self):
        self.win.blit(background_image, (0, 0))

        for block in self.blocks:
            block.draw(self.win)

        self.player.update(InputHandler(), self.blocks, self.collision_handler)
        self.player.draw(self.win)

        for enemy in self.enemies:
            enemy.update(self.player)
            enemy.draw(self.win)
            if enemy.rect.colliderect(self.player.rect):
                logging.info("Зіткнення гравця з ворогом")
                enemy.on_collision(self.player)

        if self.player.hp <= 0:
            logging.info("Гравець загинув. Кінець гри.")
            self.game = False

    def _display_start_message(self):
        self.win.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 50)
        text = font.render("Press SPACE to Start", True, (255, 255, 255))
        self.win.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2))

    def is_running(self):
        return self.game
