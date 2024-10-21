from objects import *

finish = True
pause = False
game = False

def callback_start():
    global finish, game, player, enemys, scores
    finish = False
    game = True
    scores = 0

    player = Player(player_image, 350, 250, 50, 50, 5)

    enemys.empty()
    for i in range(15):
        e = Enemy(zombie_images[0], 100, 100, 50, 50, 2)
        e.spawn()
        enemys.add(e)


bt_start = Button(win_width / 2,
                  100,
                  120,
                  50,
                  (50, 50, 100),
                  bt_start_text,
                  callback_start)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    if finish:
        win.blit(main_background_image, (0, 0))
        bt_start.update()
        bt_start.draw()

    if game:
        win.blit(background_image, (0, 0))
        for enemy in enemys:
            dx = enemy.rect.centerx - player.rect.centerx
            dy = player.rect.centery - enemy.rect.centery
            ang = -math.atan2(dy, dx) - math.pi
            enemy.update(ang)
            enemy.draw()

            if player.hitbox.colliderect(enemy.hitbox):
                damage_sound.play()
                player.hp -= enemy.damage
                enemy.spawn()

        collide = pygame.sprite.groupcollide(enemys,
                                             bullets,
                                             False,
                                             True)
        for enemy in collide:
            enemy.hp -= 1
            if enemy.hp <= 0:
                coin_sound.play()
                enemy.spawn()
                scores += 1
            

        
        player.update()
        player.draw()
        bullets.update()
        bullets.draw(win)

        if player.hp <= 0:
            game = False
            finish = True
            lose_text = ui_font.render(f"You died...",
                                True,
                                (255, 50, 50))
            
            win.blit(lose_text, (250, win_height + 5))

        pygame.draw.rect(win, background, UI)

        health = ui_font.render(f"HP: {player.hp}/100",
                                True,
                                (255, 50, 50))
        
        win.blit(health, (0, win_height + 5))

        scores_text = ui_font.render(f"coins: {scores}",
                                True,
                                (150, 200, 50))
        
        win.blit(scores_text, (win_width - 180, win_height + 5))

    pygame.display.update()
    clock.tick(FPS)