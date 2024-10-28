import pygame

pygame.init()

win_width = 700
win_height = 500
FPS = 20

win = pygame.display.set_mode((win_width, win_height + 50))
clock = pygame.time.Clock()

player_image = "textures/player.png"
block_image = "textures/block.png"
enemybullet_image = "textures/bullet.png"
playerbullet_image = "textures/allybullet.png"
zombie_image = "textures/zombie1.png"
shooter_image = "textures/zombie2.png"

background_image = pygame.transform.scale(
                    pygame.image.load('textures/background.png'),
                    (win_width, win_height)
                    )

main_background_image = pygame.transform.scale(
                    pygame.image.load('textures/main_screen.png'),
                    (win_width, win_height)
                    )


bullets = pygame.sprite.Group()
enemys = pygame.sprite.Group()


background = (150, 150, 100)
UI = pygame.Rect(0, win_height, win_width, 50)
ui_font = pygame.font.Font(None, 50)

bt_start_text = ui_font.render("START", True, (100, 255, 255))