import pygame

pygame.init()

win_width = 700
win_height = 500
FPS = 20

win = pygame.display.set_mode((win_width, win_height + 50))
clock = pygame.time.Clock()

player_image = "textures/player.png"
bullet_image = "textures/bullet.png"
zombie_images = ["textures/zombie1.png",
                 "textures/zombie2.png",
                 "textures/zombie3.png"]

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

damage_sound = pygame.mixer.Sound("sounds/damage.ogg")
coin_sound = pygame.mixer.Sound("sounds/coin.ogg")

background = (150, 150, 100)
UI = pygame.Rect(0, win_height, win_width, 50)
ui_font = pygame.font.Font(None, 50)

bt_start_text = ui_font.render("START", True, (100, 255, 255))