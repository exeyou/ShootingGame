from abc import ABC, abstractmethod
import pygame
from settings import *
import random
import math
import logging
from pygame import mixer
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
        self.shot_cooldown = 10  
        self.cooldown_timer = 0 

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

    def shoot(self):
        """Fire a bullet in the direction the player is facing."""
        if self.cooldown_timer <= 0: 

            from game_manager import GameManager
            sound = mixer.Sound('sounds/shoot.ogg')
            sound.set_volume(0.1)
            sound.play()
            angle = math.radians(self.last_angle)
            bullet = Bullet(
                self.rect.centerx, self.rect.centery, 
                self.rect.centerx + math.cos(angle) * 100,
                self.rect.centery - math.sin(angle) * 100,
                playerbullet_image 
            )
            GameManager.instance.add_player_bullet(bullet) 
            self.cooldown_timer = self.shot_cooldown 
            logging.info("Гравець випустив кулю")

    def update(self, input_handler, blocks, collision_handler):
        self.move(input_handler.get_keys())


        if input_handler.get_keys()[pygame.K_SPACE]:
            self.shoot()


        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

        collision_handler.check_collision(self, blocks)



class Block(GameSprite):
    pass

class Bullet(GameSprite):

    def __init__(self, x, y, target_x, target_y, bullet_image):
        super().__init__(bullet_image, x, y, 10, 10)
        self.speed = 10
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed

    def move(self, blocks):

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Check collision with blocks
        for block in blocks:
            if self.rect.colliderect(block.rect):
                sound = mixer.Sound('sounds/boxhit.ogg')
                sound.set_volume(0.1)
                sound.play()
                logging.info("Куля влучила в блок на позиції %s", block.rect.topleft)
                self.kill()  # Remove bullet if it hits a block

    def update(self, player, blocks):
        from game_manager import GameManager
        self.move(blocks)
        if self.rect.colliderect(player.rect) and self in GameManager.instance.enemy_bullets:
            player.hp -= 5
            logging.info("Куля влучила у гравця. Здоров'я: %d", player.hp)
            sound = mixer.Sound('sounds/playerdamaged.ogg')
            sound.set_volume(0.1)
            sound.play()
            self.kill()
        else:
            for enemy in GameManager.instance.enemies:
                if self.rect.colliderect(enemy.rect) and self in GameManager.instance.player_bullets:
                    enemy.hp -= 5
                    logging.info("Куля влучила у ворога. Здоров'я: %d", enemy.hp)
                    sound = mixer.Sound('sounds/enemyhit.ogg')
                    sound.set_volume(0.1)
                    sound.play()
                    self.kill()