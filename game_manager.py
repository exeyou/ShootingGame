import pygame
import random
import logging
from game_sprites import Player, Block, Bullet
from enemies import Zombie, Shooter
from factory import EnemyFactory
from collision import CollisionHandler
from input_handler import InputHandler
from ui import Button
from settings import player_image, block_image, zombie_image, shooter_image, enemybullet_image, win_width, win_height, background_image
from pygame import mixer
class GameManager:
    instance = None
    
    def __init__(self, win):
        self.__class__.instance = self
        self.win = win
        self.win_width, self.win_height = self.win.get_size()

        self.game_running = False
        self.game_over = False
        self.game_won = False
        self.scores = 0


        self.menu_sound_played = False
        self.lost_sound_played = False
        self.win_sound_played = False

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.player = None

        self.collision_handler = CollisionHandler()
        

        button_width, button_height = 200, 80
        self.start_button = Button(
            (self.win_width - button_width) // 2, 
            (self.win_height - button_height) // 2, 
            button_width, button_height, 
            text='Start Game'
        )


        self.restart_button = Button(
            (self.win_width - button_width) // 2,
            self.win_height // 2 + 50,
            button_width, button_height,
            text='Restart'
        )

    def start_game(self):

        mixer.stop()
        self.game_running = True
        self.game_over = False
        self.game_won = False
        self.scores = 0

 
        self.menu_sound_played = False
        self.lost_sound_played = False
        self.win_sound_played = False

        logging.info("Гра розпочата")
        self._create_objects()

    def _create_objects(self):

        self.player = Player(player_image, 350, 450, 50, 50, 5)


        self.blocks.empty()
        block_positions = [
        (100, 300), 
        (300, 250),  
        (500, 350), 
        (200, 400), 
        ]

        for pos in block_positions:
            block = Block(block_image, pos[0], pos[1], 100, 50)
            self.blocks.add(block)



        self.enemies.empty()
        for _ in range(3):
            enemy = EnemyFactory.create_enemy("zombie", random.randint(50, 550), random.randint(50, 160))
            self.enemies.add(enemy)
        for _ in range(5):
            enemy = EnemyFactory.create_enemy("shooter", random.randint(50, 550), random.randint(50, 160))
            self.enemies.add(enemy)

    def update(self):

        if self.game_over:
            self.draw_game_over_screen()
        elif self.game_won:
            self.draw_win_screen()
        elif self.game_running:
            self._run_game()
        else:
            self._display_start_message()

    def _run_game(self):
        self.win.blit(background_image, (0, 0))


        self.blocks.draw(self.win)
        self.player.update(InputHandler(), self.blocks, self.collision_handler)
        self.player.draw(self.win)

        for enemy in self.enemies:
            enemy.update(self.player, self.blocks)
            enemy.draw(self.win)

        for bullet in self.enemy_bullets:
            bullet.update(self.player, self.blocks)
            bullet.draw(self.win)

        for bullet in self.player_bullets:
            bullet.update(self.player, self.blocks)
            bullet.draw(self.win)


        self._display_player_hp()

        if self.player.hp <= 0:
            logging.info("Гравець загинув. Кінець гри.")
            self.game_running = False
            self.game_over = True

        if len(self.enemies) == 0:
            logging.info("Вітаємо! Ви перемогли!")
            self.game_running = False
            self.game_won = True

    def _display_player_hp(self):

        font = pygame.font.Font(None, 36) 
        hp_text = f"HP: {self.player.hp}"  
        text_surface = font.render(hp_text, True, (255, 0, 0)) 
        text_rect = text_surface.get_rect(topright=(self.win_width - 10, 10)) 
        self.win.blit(text_surface, text_rect) 
    def draw_game_over_screen(self):

        self.win.fill((0, 0, 0))

        if not self.lost_sound_played:
            mixer.stop()
            sound = mixer.Sound('sounds/lost.ogg')
            sound.set_volume(0.1)
            sound.play()
            self.lost_sound_played = True

        self._draw_centered_text("Ви програли!", 30, (255, 0, 0), self.win_height // 2 - 100)
        self.restart_button.draw(self.win)
        pygame.display.flip()

    def draw_win_screen(self):

        self.win.fill((0, 0, 0))

        if not self.win_sound_played:
            mixer.stop()
            sound = mixer.Sound('sounds/won.ogg')
            sound.set_volume(0.1)
            sound.play()
            self.win_sound_played = True

        self._draw_centered_text("Ви перемогли!", 30, (0, 255, 0), self.win_height // 2 - 100)
        self.restart_button.draw(self.win)
        pygame.display.flip()

    def _display_start_message(self):

        self.win.fill((0, 0, 0))
        self.win.blit(background_image, (0, 0))

        if not self.menu_sound_played:
            mixer.stop()
            sound = mixer.Sound('sounds/mainmenu.ogg')
            sound.set_volume(0.1)
            sound.play()
            self.menu_sound_played = True

        self._draw_centered_text("Shooter", 50, (255, 255, 255), 50)
        self.start_button.draw(self.win)
        pygame.display.flip()

    def _draw_centered_text(self, text, size, color, y):

        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.win_width // 2, y))
        self.win.blit(text_surface, text_rect)


    def handle_events(self, event):

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif self.start_button.is_clicked(event) and not self.game_running:
            self.start_game() 
        elif self.restart_button.is_clicked(event) and (self.game_over or self.game_won):
            self.start_game()

    def add_enemy_bullet(self, bullet):
        self.enemy_bullets.add(bullet)
    
    def add_player_bullet(self, bullet):
        self.player_bullets.add(bullet)

    def is_running(self):

        return self.game_running
