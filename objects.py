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
class EnemyBase(GameSprite, Movable, ABC):
    """Базовий клас для всіх ворогів."""
    def __init__(self, image, x, y, w, h, speed, hp):
        super().__init__(image, x, y, w, h)
        self.speed = speed
        self.hp = hp

    @abstractmethod
    def attack(self, player):
        """Метод атаки, який реалізують підкласи."""
        pass

    def move(self, player):
        """Рух ворога у напрямку гравця."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

    def update(self, player):
        self.move(player)
        self.attack(player)

class Zombie(EnemyBase):
    """Тип ворога: Зомбі."""
    def __init__(self, x, y):
        super().__init__(zombie_images[0], x, y, 50, 50, speed=2, hp=30)

    def attack(self, player):
        """Атака ближнього бою: завдає шкоду при зіткненні."""
        if self.rect.colliderect(player.rect):
            player.hp -= 10
            logging.info("Зомбі атакував гравця. Здоров'я: %d", player.hp)
            self.kill()

class Shooter(EnemyBase):
    """Тип ворога: Стрілець."""
    def __init__(self, x, y):
        super().__init__(zombie_images[1], x, y, 50, 50, speed=1, hp=20)
        self.shot_cooldown = 60 
        self.cooldown_timer = 0

    def attack(self, player):
        """Стрілець атакує з відстані."""
        if self.cooldown_timer <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
            GameManager.instance.add_enemy_bullet(bullet)
            self.cooldown_timer = self.shot_cooldown
            logging.info("Стрілець випустив кулю")
        else:
            self.cooldown_timer -= 1


class Bullet(GameSprite):
    """Куля, випущена ворогом."""
    def __init__(self, x, y, target_x, target_y):
        super().__init__(bullet_image, x, y, 10, 10)
        self.speed = 5
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed

    def move(self):
        """Куля рухається в напрямку, визначеному під час пострілу."""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    def update(self, player):
        self.move()
        if self.rect.colliderect(player.rect):
            player.hp -= 5
            logging.info("Куля влучила у гравця. Здоров'я: %d", player.hp)
            self.kill()


class EnemyFactory:
    """Фабрика для створення ворогів."""
    @staticmethod
    def create_enemy(enemy_type, x, y):
        if enemy_type == "zombie":
            return Zombie(x, y)
        elif enemy_type == "shooter":
            return Shooter(x, y)
        else:
            raise ValueError(f"Невідомий тип ворога: {enemy_type}")
class GameManager:
    instance = None 
    def __init__(self, win):
        self.__class__.instance = self
        self.win = win
        self.game = False
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
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

        self.enemies.empty()
        for _ in range(5):
            enemy_type = random.choice(["zombie", "shooter"])
            enemy = EnemyFactory.create_enemy(enemy_type, random.randint(50, 750), random.randint(50, 550))
            self.enemies.add(enemy)

    def update(self):
        if self.game:
            self._run_game()
        else:
            self._display_start_message()

    def _run_game(self):
        self.win.blit(background_image, (0, 0))
        self._spawn_enemies()
        self.win.blit(background_image, (0, 0))

        for block in self.blocks:
            block.draw(self.win)

        self.player.update(InputHandler(), self.blocks, self.collision_handler)
        self.player.draw(self.win)

        for enemy in self.enemies:
            enemy.update(self.player)
            enemy.draw(self.win)

        for bullet in self.enemy_bullets:
            bullet.update(self.player)
            bullet.draw(self.win)

        if self.player.hp <= 0:
            logging.info("Гравець загинув. Кінець гри.")
            self.game = False
    def _display_start_message(self):
        self.win.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 50)
        text = font.render("Press SPACE to Start", True, (255, 255, 255))
        self.win.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2))
    def _spawn_enemies(self):
        """Спавнить нових ворогів випадково."""
        if len(self.enemies) < 5 and random.random() < 0.01:
            enemy_type = random.choice(["zombie", "shooter"])
            enemy = EnemyFactory.create_enemy(enemy_type, random.randint(50, 750), random.randint(50, 550))
            self.enemies.add(enemy)
    def add_enemy_bullet(self, bullet):
        """Додає кулю до групи куль."""
        self.enemy_bullets.add(bullet)

    def is_running(self):
        return self.game

