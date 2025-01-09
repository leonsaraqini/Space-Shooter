from __future__ import division
import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')


WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10


TOTAL_GAME_TIME = 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()


font_name = pygame.font.match_font('arial')


def main_menu():
    global screen, score, game_over, all_sprites, mobs, bullets, powerups, player, start_time

    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    score = 0
    game_over = False
    start_time = pygame.time.get_ticks()

    pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT))

    screen.blit(title, (0, 0))
    pygame.display.update()


    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH / 2, HEIGHT / 2)
            draw_text(screen, "or [Q] To Quit", 30, WIDTH / 2, (HEIGHT / 2) + 40)
            pygame.display.update()

    ready = pygame.mixer.Sound(path.join(sound_folder, 'getready.ogg'))
    ready.play()
    screen.fill(BLACK)
    draw_text(screen, "GET READY!", 40, WIDTH / 2, HEIGHT / 2)
    pygame.display.update()
    pygame.time.wait(2000)

    for i in range(8):
        newmob(base_size=0.5)


background_game_over = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_game_over_rect = background_game_over.get_rect()


def game_over_screen(screen, score, message):
    pygame.mixer.music.stop()
    try:
        game_over_sound = pygame.mixer.Sound(path.join(sound_folder, 'game_over.ogg'))
        game_over_sound.play()
    except:
        pass


    screen.blit(background_game_over, background_game_over_rect)


    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 0))

    draw_text(screen, message, 40, WIDTH / 2 + 2, HEIGHT / 4 + 2)
    draw_text(screen, f"Score: {score}", 30, WIDTH / 2 + 2, HEIGHT / 2 + 2)
    draw_text(screen, "Press [R] to Restart or [Q] to Quit", 30, WIDTH / 2 + 2, (HEIGHT / 2) + 42)


    draw_text(screen, message, 40, WIDTH / 2, HEIGHT / 4, WHITE)
    draw_text(screen, f"Score: {score}", 30, WIDTH / 2, HEIGHT / 2, WHITE)
    draw_text(screen, "Press [R] to Restart or [Q] to Quit", 30, WIDTH / 2, (HEIGHT / 2) + 40, WHITE)

    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    return True  # Indicate restart
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()


def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    pct = max(pct, 0)
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def newmob(base_size=1.0):
    """Create a new asteroid (mob) with a size multiplier based on base_size."""
    mob_element = Mob(base_size)
    all_sprites.add(mob_element)
    mobs.add(mob_element)


def draw_score(surf, score, x, y):
    draw_text(surf, "Score: " + str(score), 30, x + 60, y + 5)  # Draw the score


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):

        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()


        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30

        self.speedx = 0



        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5


        if keystate[pygame.K_SPACE]:
            self.shoot()


        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
    def __init__(self, base_size=1.0):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)

        # Apply base size multiplier (uniform size)
        final_size = base_size  # No random size

        # Scale the image uniformly based on base_size
        width = int(self.image_orig.get_width() * final_size)
        height = int(self.image_orig.get_height() * final_size)
        self.image_orig = pygame.transform.scale(self.image_orig, (width, height))

        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .90 / 2)

        # Fixed spawn position above the screen
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = -150  # Fixed spawn y-position

        # Initial slow speed
        self.speedy = random.randrange(1, 3)  # Slow initial speed
        self.speedx = 0  # No horizontal movement initially

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50:  # in milliseconds
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy


        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:

            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = -150

            global size_multiplier
            base_speed = random.randrange(1, 3)
            self.speedy = base_speed * size_multiplier

            # Optionally, increase horizontal speed slightly as well
            self.speedx = random.randrange(-1, 1)



class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy

        if self.rect.top > HEIGHT:
            self.kill()



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):

        self.rect.y += self.speedy

        if self.rect.bottom < 0:
            self.kill()



class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):

        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()



background = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_rect = background.get_rect()


player_img = pygame.image.load(path.join(img_dir, 'spaceship.png'))

player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
meteor_images = []
meteor_list = [
    'meteorBrown_big1.png',
    'meteorBrown_big2.png',
    'meteorBrown_med1.png',
    'meteorBrown_med3.png',
    'meteorBrown_small1.png',
    'meteorBrown_small2.png',
    'meteorBrown_tiny1.png'
]

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())


explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)

    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)


powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()


shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))

pygame.mixer.music.set_volume(0.2)

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))


menu_display = True
while True:
    if menu_display:
        main_menu()
        pygame.time.wait(2000)

        pygame.mixer.music.stop()

        pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
        pygame.mixer.music.play(-1)

        menu_display = False


    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False


    if not game_over:
        all_sprites.update()


        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        remaining_time = max(TOTAL_GAME_TIME - elapsed_time, 0)


        time_progress = 1 - (remaining_time / TOTAL_GAME_TIME)
        size_multiplier = 1 + time_progress * 1.5


        globals()['size_multiplier'] = size_multiplier


        while len(mobs) < 8:
            newmob(base_size=0.5 * size_multiplier)

        if remaining_time <= 0:
            if game_over_screen(screen, score, "CONGRATS you won!"):
                menu_display = True
                continue


        timer_text = "{:02}:{:02}".format(int(remaining_time // 60), int(remaining_time % 60))


        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 50 - hit.radius
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)

            newmob(base_size=0.5 * size_multiplier)


        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)

            newmob(base_size=0.5 * size_multiplier)
            if player.shield <= 0:
                player_die_sound.play()
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.shield = 100

        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                player.powerup()

        if player.lives == 0 and not hasattr(player, 'death_explosion'):
            if game_over_screen(screen, score, "Game Over!"):
                menu_display = True
                continue
        elif player.lives == 0 and hasattr(player, 'death_explosion') and not death_explosion.alive():
            if game_over_screen(screen, score, "Game Over!"):
                menu_display = True
                continue

    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_score(screen, score, WIDTH / 2, 10)
    if not game_over:
        draw_text(screen, timer_text, 18, 10, 20)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()




