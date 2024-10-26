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
    
    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Player(GameSprite, Movable):
    def __init__(self, image, x, y, w, h, speed):
        super().__init__(image, x, y, w, h)
        self.speed = speed
        self.hp = 100
        self.last_angle = 0
        logging.info("Гравець створений на позиції (%d, %d)", x, y)

    def move(self, keys):
        old_position = self.rect.topleft
        new_angle = self.last_angle
        
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            new_angle = 180
        elif keys[pygame.K_d]:
            self.rect.x += self.speed
            new_angle = 0 
        elif keys[pygame.K_w]:
            self.rect.y -= self.speed
            new_angle = 90
        elif keys[pygame.K_s]:
            self.rect.y += self.speed
            new_angle = 270
        
        if new_angle != self.last_angle:
            self.rotate(new_angle - self.last_angle)
            self.last_angle = new_angle
        
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

    @abstractmethod
    def move(self, player):
        """Унікальний рух для кожного ворога."""
        pass

    def update(self, player):
        self.move(player)
        self.attack(player)

class Zombie(EnemyBase):
    """Тип ворога: Зомбі."""
    def __init__(self, x, y):
        super().__init__(zombie_images[0], x, y, 50, 50, speed=2, hp=30)

    def move(self, player):
        """Рух зомбі: слідує за гравцем лінійно."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

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

    def move(self, player):
        """Стрілець намагається підтримувати дистанцію від гравця."""
        distance = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        if distance < 150:
            dx = self.rect.centerx - player.rect.centerx
            dy = self.rect.centery - player.rect.centery
        else:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

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

class Button:
    def __init__(self, x, y, width, height, text='', color=(0, 128, 255), hover_color=(75, 200, 255), text_color=(255, 255, 255), font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.clicked = False

    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            if self.rect.collidepoint(event.pos):
                return True
        return False

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
        self.game_running = False
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.player = None
        self.scores = 0
        self.collision_handler = CollisionHandler()

        self.start_button = Button(200, 150, 200, 80, text='Start Game')

    def start_game(self):
        """Start the game and initialize objects."""
        self.game_running = True
        self.scores = 0
        logging.info("Гра розпочата")
        self._create_objects()

    def _create_objects(self):
        """Create player, blocks, and enemies."""
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
        """Update game state and draw the current frame."""
        if self.game_running:
            self._run_game()
        else:
            self._display_start_message()

    def _run_game(self):
        """Main game loop logic."""
        self.win.blit(background_image, (0, 0))

        self.blocks.draw(self.win)
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
            self.game_running = False
    def _display_start_message(self):
        """Display the start message and button."""
        self.win.fill((0, 0, 0)) 
        self.win.blit(background_image, (0, 0))
        self.start_button.draw(self.win)

    def handle_events(self, event):
        """Handle events like button clicks."""
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif self.start_button.is_clicked(event) and self.game_running != True:
            self.start_game() 

    def add_enemy_bullet(self, bullet):
        """Add a bullet to the enemy bullets group."""
        self.enemy_bullets.add(bullet)

    def is_running(self):
        """Check if the game is running."""
        return self.game_running

