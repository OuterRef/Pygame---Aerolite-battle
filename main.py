import pygame
import os
import sys
import random

pygame.init()

# Global Consts.
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

AEROLITE = [
    pygame.image.load(os.path.join("img/aerolites", "falling_aerolite.png")),   # 0 - unbreakable
    pygame.image.load(os.path.join("img/aerolites", "aerolite1.png")),          # 1
    pygame.image.load(os.path.join("img/aerolites", "aerolite2.png"))           # 2
]
EXPLOSION = pygame.image.load(os.path.join("img/effect", "explosion120.png"))
AEROPLANE = pygame.image.load(os.path.join("img/figure", "plane.png"))
BULLET = pygame.image.load(os.path.join("img/figure", "freaking_cool_bullet.png"))
GAMEOVER = pygame.image.load(os.path.join("img/effect", "gameover.png"))
FONT = pygame.font.Font("img/times-ro.ttf", 20)

class Aeroplane:
    X_POS = (SCREEN_WIDTH - 242) // 2
    Y_POS = SCREEN_HEIGHT - 90
    VEL = 15

    def __init__(self, img=AEROPLANE):
        self.img = img
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, self.img.get_width(), self.img.get_height())
        self.fire = False
    
    def move_right(self):
        if self.rect.x <= SCREEN_WIDTH - self.img.get_width() - 200:
            self.rect.x += self.VEL

    def move_left(self):
        if self.rect.x >= 0:
            self.rect.x -= self.VEL
    
    def attack(self):
        global ammo
        if ammo > 0:
            bullets.append(
                Bullet(position=(self.rect.x, self.rect.y+40))
            )
            bullets.append(
                Bullet(position=(self.rect.x+self.img.get_width()-7, self.rect.y+40))
            )
            ammo -= 1

    def draw(self, screen):
        screen.blit(self.img, (self.rect.x, self.rect.y))
        if hit_box:
            pygame.draw.rect(screen, (30,144,255), self.rect, 2)

class Bullet:
    BULLET_VEL = 40

    def __init__(self, position, img=BULLET):
        self.x, self.y = position
        self.img = img
        self.rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        self.alive = True

    def update(self):
        if self.rect.y >= -self.img.get_height():
            self.rect.y -= self.BULLET_VEL
            self.draw(SCREEN)
        else:
            self.alive = False

    def draw(self, screen):
        screen.blit(self.img, (self.rect.x, self.rect.y))

class Aerolite:
    def __init__(self):
        self.type = random.randint(0, 2)
        self.img = AEROLITE[self.type]
        self.vel = game_speed + random.randint(-10, -5)
        if self.type != 0:
            self.rotation = random.randint(0,180)
        else:
            self.rotation = 0
        self.rotated_img = pygame.transform.rotate(self.img, self.rotation)
        self.rect = self.rotated_img.get_rect(center=self.img.get_rect().center)
        self.rect.x = random.randint(0, SCREEN_WIDTH-self.rotated_img.get_width()-200)
        self.rect.y = -self.img.get_height()
        self.alive = True
    
    def update(self):
        if self.rect.y > SCREEN_HEIGHT + self.img.get_height():
            self.alive = False
        if self.alive == True:
            self.rect.y += self.vel
            self.draw(SCREEN)
        else:
            self.explode(SCREEN)

    def explode(self, screen):
        screen.blit(EXPLOSION, self.rect)

    def draw(self, screen):
        screen.blit(self.rotated_img, self.rect)
        if hit_box:
            pygame.draw.rect(screen, (238,0,0), self.rect, 2)

def statistics():
    text_1 = FONT.render(f"Score: {point}", True, (0,0,0))
    text_2 = FONT.render(f"Game Speed: {str(game_speed)}", True, (0,0,0))
    text_3 = FONT.render(f"Ammo: {str(ammo)}", True, (255 if ammo <= 10 else 0,0,0))

    SCREEN.blit(text_1, (SCREEN_WIDTH - 180, 30))
    SCREEN.blit(text_2, (SCREEN_WIDTH - 180, 60))
    SCREEN.blit(text_3, (SCREEN_WIDTH - 180, 550))

def background():
    SCREEN.fill((255, 255, 255))
    pygame.draw.line(SCREEN, (0,0,0), (SCREEN_WIDTH-198, 0), (SCREEN_WIDTH-198, SCREEN_HEIGHT), 2)

# main loop
def main():
    global game_speed, point, hit_box, show_line, cheating, ammo
    global aeroplane, bullets, aerolites

    clock = pygame.time.Clock()

    aeroplane = Aeroplane()
    bullets = []
    aerolites = []

    game_speed = 20
    point = 0
    ammo = 30
    hit_box = False
    show_line = False
    cheating = False

    tick = 0
    run = True
    while run:
        game_speed = point // 10 + 20
        if ammo < 20 and tick % 10 == 0:
            ammo += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:     # show hit-box
                    hit_box = not hit_box
                if event.key == pygame.K_l:     # show lines from plane to aerolites
                    show_line = not show_line
        
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_RIGHT]:
            aeroplane.move_right()
        if user_input[pygame.K_LEFT]:
            aeroplane.move_left()
        if user_input[pygame.K_SPACE] and tick % 3 == 0:
            aeroplane.attack()

        background()
        statistics()

        aeroplane.draw(SCREEN)
        
        for bullet in bullets:
            bullet.update()
        bullets = [bullet for bullet in bullets if bullet.alive]

        gen_aerolite = random.randint(0,1000)
        if len(aerolites) == 0 or gen_aerolite <= game_speed:
            # print("generated an aerolite")
            aerolites.append(Aerolite())

        for aerolite in aerolites:
            if aeroplane.rect.colliderect(aerolite.rect) and not cheating:
                run = False
            for bullet in bullets:
                if bullet.rect.colliderect(aerolite.rect):
                    if aerolite.type != 0:
                        aerolite.alive = False
                        point += 1
                    bullet.alive = False
            aerolite.update()
        aerolites = [aerolite for aerolite in aerolites if aerolite.alive]
        # print(len(aerolites))

        if show_line:
            for aerolite in aerolites:
                pygame.draw.line(SCREEN, (0,0,0), aeroplane.rect.center, aerolite.rect.center)

        tick += 1
        # 30 fps
        clock.tick(30)
        pygame.display.update()

def gameover():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
        background()
        statistics()
        SCREEN.blit(GAMEOVER, ((SCREEN_WIDTH-200-GAMEOVER.get_width())/2, (SCREEN_HEIGHT-GAMEOVER.get_height())/2))
        prompt_text = FONT.render("Press R to respawn", True, (255,0,0))
        SCREEN.blit(prompt_text, (210, 430))
        pygame.display.update()


if __name__ == "__main__":
    main()
    gameover()

