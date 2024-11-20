import pygame
import random  # Tambahkan ini untuk menggunakan choice
from pygame.locals import *

# Inisialisasi pygame
pygame.init()

# Ukuran layar
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Warna
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Variabel game
running = True
paused = False
score = 0
level = 1
shake_duration = 0
shake_offset = (0, 0)

# Sound effects
shoot_sound = pygame.mixer.Sound("laser_S5c8iCH.mp3")
collision_sound = pygame.mixer.Sound("stationary-kill_gDwMUvN.mp3")


# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.health = 100

    def update(self, pressed_keys=None):
        if pressed_keys:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -5)
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, 5)

        # Batasi gerakan pemain dalam layar
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw_health_bar(self, surface):
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top - 10, 50, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top - 10, self.health * 0.5, 5))



# Peluru
class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, shape):
        super().__init__()
        self.color = color
        self.shape = shape
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(player.rect.centerx, player.rect.top))

        if shape == "square":
            pygame.draw.rect(self.image, color, (0, 0, 10, 10))
        elif shape == "triangle":
            pygame.draw.polygon(self.image, color, [(5, 0), (10, 10), (0, 10)])
        elif shape == "circle":
            pygame.draw.circle(self.image, color, (5, 5), 5)

    def update(self):
        self.rect.move_ip(0, -10)
        if self.rect.bottom < 0:
            self.kill()

# Musuh
class Enemy(pygame.sprite.Sprite):
    def __init__(self, color, shape):
        super().__init__()
        self.color = color
        self.shape = shape
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH - 20), 0))

        if shape == "square":
            pygame.draw.rect(self.image, color, (0, 0, 30, 30))
        elif shape == "triangle":
            pygame.draw.polygon(self.image, color, [(15, 0), (30, 30), (0, 30)])
        elif shape == "circle":
            pygame.draw.circle(self.image, color, (15, 15), 15)

    def update(self):
        self.rect.move_ip(0, 5)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Efek Screen Shake
def screen_shake():
    global shake_duration, shake_offset
    if shake_duration > 0:
        shake_offset = (random.randint(-5, 5), random.randint(-5, 5))
        shake_duration -= 1
    else:
        shake_offset = (0, 0)

# Fungsi menembak
def shoot_bullet(bullet_type):
    if bullet_type == 'J':
        bullet = Bullet(RED, "square")
    elif bullet_type == 'K':
        bullet = Bullet(GREEN, "triangle")
    elif bullet_type == 'L':
        bullet = Bullet(BLUE, "circle")
    bullets.add(bullet)
    all_sprites.add(bullet)
    shoot_sound.play()

# Setup sprite
player = Player()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
all_sprites.add(player)

# Clock
clock = pygame.time.Clock()

# Spawning musuh dengan berbagai tipe
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 1000)

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_j:
                shoot_bullet('J')
            elif event.key == K_k:
                shoot_bullet('K')
            elif event.key == K_l:
                shoot_bullet('L')
        elif event.type == ADDENEMY:
            enemy_type = random.choice(['square', 'triangle', 'circle'])  # Menggunakan random.choice
            if enemy_type == "square":
                new_enemy = Enemy(RED, "square")
            elif enemy_type == "triangle":
                new_enemy = Enemy(GREEN, "triangle")
            elif enemy_type == "circle":
                new_enemy = Enemy(BLUE, "circle")
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

    # Update player dengan input keyboard
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    # Update semua sprite
    bullets.update()
    enemies.update()

    # Collision detection
    for bullet in bullets:
        enemy_hit = pygame.sprite.spritecollideany(bullet, enemies)
        if enemy_hit:
            # Periksa kecocokan warna dan bentuk
            if (bullet.color == enemy_hit.color) and (bullet.shape == enemy_hit.shape):
                bullet.kill()
                enemy_hit.kill()
                score += 10
                collision_sound.play()
            else:
                # Efek jika peluru tidak cocok
                bullet.kill()
            
    # Collision detection: Player and enemies
    enemy_hit = pygame.sprite.spritecollideany(player, enemies)
    if enemy_hit:
        player.health -= 10  # Kurangi health pemain
        print(f"Player health: {player.health}")  # Debugging: cek nilai health
        enemy_hit.kill()  # Hancurkan musuh yang bertabrakan
        print("Enemy destroyed!")  # Debugging: konfirmasi musuh dihancurkan
        if player.health <= 0:
            print("Game over!")  # Debugging: jika HP habis
            running = False  # Hentikan permainan
        shake_duration = 10  # Efek getaran layar



    # Gambar latar belakang dan sprite
    screen.fill((BLACK))
    all_sprites.draw(screen)
    player.draw_health_bar(screen) 

    # Tampilkan skor
    font = pygame.font.Font(None, 36)
    text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(text, (10, 10))

    # Update layar
    pygame.display.flip()

    # Frame rate
    clock.tick(30)

pygame.quit()
