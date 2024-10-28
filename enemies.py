import pygame
import random
from abc import ABC, abstractmethod
import math
import os
from game_sprites import GameSprite, Movable, Bullet
from settings import *
import logging
from pygame import mixer
def load_death_animation(scale_to):
    frames = []
    for i in range(7):
        path = f"animations/explosion/{i}.png"
        frame = pygame.image.load(path).convert_alpha()

        scaled_frame = pygame.transform.scale(frame, scale_to)
        frames.append(scaled_frame)
    return frames


class EnemyBase(GameSprite, Movable, ABC):

    def __init__(self, image, x, y, w, h, speed, hp, dead):
        super().__init__(image, x, y, w, h)
        self.speed = speed
        self.hp = hp
        self.dead = False
        self.animation_index = 0 
        self.animation_timer = 0 


        self.death_animation = load_death_animation((w, h))  
    @abstractmethod
    def attack(self, player):
        pass

    @abstractmethod
    def move(self, player, blocks):
        pass

    def update(self, player, blocks):
        if self.hp > 0:
            self.move(player, blocks)
            self.attack(player)
        else:
            self.play_death_animation()

    def play_death_animation(self):
        """Play the death animation at the enemy's position."""
        sound = mixer.Sound('sounds/enemydeath.ogg')
        sound.set_volume(0.1)
        sound.play()
        if self.animation_index < len(self.death_animation):
            if self.animation_timer <= 0:

                current_frame = self.death_animation[self.animation_index]
                self.image = current_frame

                win.blit(current_frame, self.rect.topleft)

                self.animation_index += 1
                self.animation_timer = 0.5
            else:
                self.animation_timer -= 1
        else:
            self.kill()

class Zombie(EnemyBase):
    def __init__(self, x, y):
        super().__init__(zombie_image, x, y, 50, 50, speed=2, hp=30, dead=False)

    def move(self, player, blocks):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        new_x = self.rect.x + math.cos(angle) * self.speed
        new_y = self.rect.y + math.sin(angle) * self.speed
        new_rect = self.rect.move(new_x - self.rect.x, new_y - self.rect.y)

        for block in blocks:
            if new_rect.colliderect(block.rect):

                if random.choice([True, False]): 
                    angle += math.pi / 2 
                else:
                    angle -= math.pi / 2 
                

                new_x = self.rect.x + math.cos(angle) * self.speed
                new_y = self.rect.y + math.sin(angle) * self.speed
                new_rect = self.rect.move(new_x - self.rect.x, new_y - self.rect.y)


                if new_rect.colliderect(block.rect):
                    return


        self.rect.x = new_x
        self.rect.y = new_y

    def attack(self, player):
        if self.rect.colliderect(player.rect):
            self.kill()
            player.hp -= 10
            sound = mixer.Sound('sounds/saw.ogg')
            sound.set_volume(0.1)
            sound.play()


class Shooter(EnemyBase):
    def __init__(self, x, y):
        super().__init__(shooter_image, x, y, 50, 50, speed=1, hp=20, dead=False)
        self.shot_cooldown = 60
        self.cooldown_timer = 0

    def move(self, player, blocks):
        distance = math.hypot(
            player.rect.centerx - self.rect.centerx, 
            player.rect.centery - self.rect.centery
        )
        if distance < 150:
            dx = self.rect.centerx - player.rect.centerx
            dy = self.rect.centery - player.rect.centery
        else:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

        angle = math.atan2(dy, dx)

        new_x = self.rect.x + math.cos(angle) * self.speed
        new_y = self.rect.y + math.sin(angle) * self.speed
        new_rect = self.rect.move(new_x - self.rect.x, new_y - self.rect.y)

        for block in blocks:
            if new_rect.colliderect(block.rect):

                if random.choice([True, False]):
                    angle += math.pi / 2 
                else:
                    angle -= math.pi / 2

                new_x = self.rect.x + math.cos(angle) * self.speed
                new_y = self.rect.y + math.sin(angle) * self.speed
                new_rect = self.rect.move(new_x - self.rect.x, new_y - self.rect.y)

                if new_rect.colliderect(block.rect):
                    return


        self.rect.x = new_x
        self.rect.y = new_y

    def attack(self, player):
        from game_manager import GameManager
        if self.cooldown_timer <= 0:
            bullet = Bullet(
                self.rect.centerx, self.rect.centery, 
                player.rect.centerx, player.rect.centery, 
                enemybullet_image
            )
            GameManager.instance.add_enemy_bullet(bullet)
            self.cooldown_timer = self.shot_cooldown
            logging.info("Стрілець випустив кулю")
        else:
            self.cooldown_timer -= 1