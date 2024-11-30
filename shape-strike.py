import pygame
import random  # Tambahkan ini untuk menggunakan choice
from pygame.locals import *
import os

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
shoot_sound = pygame.mixer.Sound("laser.mp3")
collision_sound = pygame.mixer.Sound("kill.mp3")


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
            if pressed_keys[K_a]:  # Gerak ke kiri dengan tombol 'A'
                self.rect.move_ip(-10, 0)
            if pressed_keys[K_d]:  # Gerak ke kanan dengan tombol 'D'
                self.rect.move_ip(10, 0)
            if pressed_keys[K_w]:  # Gerak ke atas dengan tombol 'W'
                self.rect.move_ip(0, -10)
            if pressed_keys[K_s]:  # Gerak ke bawah dengan tombol 'S'
                self.rect.move_ip(0, 10)

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


# Menu states
MENU_MAIN = 0
MENU_PLAY = 1
MENU_SHIP_SELECTION = 2
MENU_PAUSE = 3
current_menu = MENU_MAIN

# Kapal yang tersedia
ship_options = [
    "ship1.png",
    "ship2.png",
    "ship3.png"
]
custom_ship = None  # Kapal custom pengguna
selected_ship = ship_options[0]  # Kapal default

def draw_main_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    start_text = font.render("Start", True, WHITE)
    select_ship_text = font.render("Pilih Kapal", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)

    screen.blit(start_text, (SCREEN_WIDTH // 2 - 50, 200))
    screen.blit(select_ship_text, (SCREEN_WIDTH // 2 - 80, 300))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - 50, 400))
    pygame.display.flip()

def draw_pause_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    continue_text = font.render("Lanjut", True, WHITE)
    exit_text = font.render("Keluar", True, WHITE)

    screen.blit(continue_text, (SCREEN_WIDTH // 2 - 50, 200))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - 50, 300))
    pygame.display.flip()

def draw_ship_selection():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    text = font.render("Pilih Kapal", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, 50))

    # Tampilkan opsi kapal
    for i, ship in enumerate(ship_options):
        ship_image = pygame.image.load(ship).convert_alpha()
        ship_image = pygame.transform.scale(ship_image, (100, 100))
        screen.blit(ship_image, (150 + i * 150, 200))
    
    # Tampilkan opsi kapal custom jika ada
    if custom_ship:
        custom_image = pygame.image.load(custom_ship).convert_alpha()
        custom_image = pygame.transform.scale(custom_image, (100, 100))
        screen.blit(custom_image, (600, 200))

    pygame.display.flip()

def load_custom_ship():
    global custom_ship
    custom_ship = "custom_ship.png"  # Asumsikan file diletakkan manual
    ship_options.append(custom_ship)

def main_menu_logic():
    global current_menu, running
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 250:  # Start
                current_menu = MENU_PLAY
            elif 300 < y < 350:  # Pilih Kapal
                current_menu = MENU_SHIP_SELECTION
            elif 400 < y < 450:  # Exit
                running = False

def pause_menu_logic():
    global current_menu, running, paused
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 250:  # Lanjut
                paused = False
                current_menu = MENU_PLAY
            elif 300 < y < 350:  # Keluar
                current_menu = MENU_MAIN

def ship_selection_logic():
    global current_menu, selected_ship
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 300:
                selected_ship = ship_options[0]
            elif 350 < y < 450:
                selected_ship = ship_options[1]
            elif 500 < y < 600:
                selected_ship = ship_options[2]
            elif custom_ship and 650 < x < 750 and 200 < y < 300:
                selected_ship = custom_ship
            current_menu = MENU_MAIN


def reset_game():
    """Mengatur ulang variabel dan sprite ke kondisi awal."""
    global player, all_sprites, enemies, bullets, score

    # Reset variabel game
    score = 0

    # Hapus semua sprite
    all_sprites.empty()
    enemies.empty()
    bullets.empty()

    # Buat ulang pemain dan tambahkan ke grup sprite
    player = Player()
    all_sprites.add(player)


while running:
    if current_menu == MENU_MAIN:  # Menu Utama
        draw_main_menu()  # Gambar menu utama
        main_menu_logic()  # Tangani logika menu utama

    elif current_menu == MENU_SHIP_SELECTION:  # Menu Pilih Kapal
        draw_ship_selection()  # Gambar menu pilih kapal
        ship_selection_logic()  # Tangani logika menu pilih kapal

    elif current_menu == MENU_PLAY:  # Game Dimulai
        if paused:  # Jika game dalam keadaan pause
            draw_pause_menu()  # Gambar menu pause
            option = pause_menu_logic()  # Tangani input dari menu pause
            
            if option == "resume":  # Lanjutkan permainan
                paused = False
            elif option == "quit":  # Reset game dan kembali ke menu utama
                reset_game() 
                current_menu = MENU_MAIN  # Kembali ke menu utama

        else:  # Jika game sedang berjalan
            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:  # Jika pengguna menutup jendela
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # Jika ESC ditekan
                        paused = True
                    elif event.key == K_j:  # Menembak dengan peluru 'J'
                        shoot_bullet('J')
                    elif event.key == K_k:  # Menembak dengan peluru 'K'
                        shoot_bullet('K')
                    elif event.key == K_l:  # Menembak dengan peluru 'L'
                        shoot_bullet('L')
                elif event.type == ADDENEMY:  # Menambahkan musuh baru
                    enemy_type = random.choice(['square', 'triangle', 'circle'])
                    if enemy_type == "square":
                        new_enemy = Enemy(RED, "square")
                    elif enemy_type == "triangle":
                        new_enemy = Enemy(GREEN, "triangle")
                    elif enemy_type == "circle":
                        new_enemy = Enemy(BLUE, "circle")
                    enemies.add(new_enemy)
                    all_sprites.add(new_enemy)

            # Update sprite dan logika permainan
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys)
            bullets.update()
            enemies.update()

            # Deteksi tabrakan peluru dan musuh
            for bullet in bullets:
                enemy_hit = pygame.sprite.spritecollideany(bullet, enemies)
                if enemy_hit:
                    if (bullet.color == enemy_hit.color) and (bullet.shape == enemy_hit.shape):
                        bullet.kill()
                        enemy_hit.kill()
                        score += 10
                        collision_sound.play()
                    else:
                        bullet.kill()

            # Deteksi tabrakan pemain dan musuh
            enemy_hit = pygame.sprite.spritecollideany(player, enemies)
            if enemy_hit:
                player.health -= 10
                enemy_hit.kill()
                if player.health <= 0:
                    reset_game()  # Reset game jika pemain kalah
                    current_menu = MENU_MAIN

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

    # Batasi frame rate
    clock.tick(30)

pygame.quit()

import pygame
import random  # Tambahkan ini untuk menggunakan choice
from pygame.locals import *
import os

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
shoot_sound = pygame.mixer.Sound("laser.mp3")
collision_sound = pygame.mixer.Sound("kill.mp3")


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
            if pressed_keys[K_a]:  # Gerak ke kiri dengan tombol 'A'
                self.rect.move_ip(-20, 0)
            if pressed_keys[K_d]:  # Gerak ke kanan dengan tombol 'D'
                self.rect.move_ip(20, 0)
            if pressed_keys[K_w]:  # Gerak ke atas dengan tombol 'W'
                self.rect.move_ip(0, -20)
            if pressed_keys[K_s]:  # Gerak ke bawah dengan tombol 'S'
                self.rect.move_ip(0, 20)

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


# Menu states
MENU_MAIN = 0
MENU_PLAY = 1
MENU_SHIP_SELECTION = 2
MENU_PAUSE = 3
current_menu = MENU_MAIN

# Kapal yang tersedia
ship_options = [
    "ship1.png",
    "ship2.png",
    "ship3.png"
]
custom_ship = None  # Kapal custom pengguna
selected_ship = ship_options[0]  # Kapal default

def draw_main_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    start_text = font.render("Start", True, WHITE)
    select_ship_text = font.render("Pilih Kapal", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)

    screen.blit(start_text, (SCREEN_WIDTH // 2 - 50, 200))
    screen.blit(select_ship_text, (SCREEN_WIDTH // 2 - 80, 300))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - 50, 400))
    pygame.display.flip()

def draw_pause_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    continue_text = font.render("Lanjut", True, WHITE)
    exit_text = font.render("Keluar", True, WHITE)

    screen.blit(continue_text, (SCREEN_WIDTH // 2 - 50, 200))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - 50, 300))
    pygame.display.flip()

def draw_ship_selection():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    text = font.render("Pilih Kapal", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, 50))

    # Tampilkan opsi kapal
    for i, ship in enumerate(ship_options):
        ship_image = pygame.image.load(ship).convert_alpha()
        ship_image = pygame.transform.scale(ship_image, (100, 100))
        screen.blit(ship_image, (150 + i * 150, 200))
    
    # Tampilkan opsi kapal custom jika ada
    if custom_ship:
        custom_image = pygame.image.load(custom_ship).convert_alpha()
        custom_image = pygame.transform.scale(custom_image, (100, 100))
        screen.blit(custom_image, (600, 200))

    pygame.display.flip()

def load_custom_ship():
    global custom_ship
    custom_ship = "custom_ship.png"  # Asumsikan file diletakkan manual
    ship_options.append(custom_ship)

def main_menu_logic():
    global current_menu, running
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 250:  # Start
                current_menu = MENU_PLAY
            elif 300 < y < 350:  # Pilih Kapal
                current_menu = MENU_SHIP_SELECTION
            elif 400 < y < 450:  # Exit
                running = False

def pause_menu_logic():
    global current_menu, running, paused
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 250:  # Lanjut
                paused = False
                current_menu = MENU_PLAY
            elif 300 < y < 350:  # Keluar
                current_menu = MENU_MAIN

def ship_selection_logic():
    global current_menu, selected_ship
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 300:
                selected_ship = ship_options[0]
            elif 350 < y < 450:
                selected_ship = ship_options[1]
            elif 500 < y < 600:
                selected_ship = ship_options[2]
            elif custom_ship and 650 < x < 750 and 200 < y < 300:
                selected_ship = custom_ship
            current_menu = MENU_MAIN


def reset_game():
    """Mengatur ulang variabel dan sprite ke kondisi awal."""
    global player, all_sprites, enemies, bullets, score

    # Reset variabel game
    score = 0

    # Hapus semua sprite
    all_sprites.empty()
    enemies.empty()
    bullets.empty()

    # Buat ulang pemain dan tambahkan ke grup sprite
    player = Player()
    all_sprites.add(player)


while running:
    if current_menu == MENU_MAIN:  # Menu Utama
        draw_main_menu()  # Gambar menu utama
        main_menu_logic()  # Tangani logika menu utama

    elif current_menu == MENU_SHIP_SELECTION:  # Menu Pilih Kapal
        draw_ship_selection()  # Gambar menu pilih kapal
        ship_selection_logic()  # Tangani logika menu pilih kapal

    elif current_menu == MENU_PLAY:  # Game Dimulai
        if paused:  # Jika game dalam keadaan pause
            draw_pause_menu()  # Gambar menu pause
            option = pause_menu_logic()  # Tangani input dari menu pause
            
            if option == "resume":  # Lanjutkan permainan
                paused = False
            elif option == "quit":  # Reset game dan kembali ke menu utama
                reset_game() 
                current_menu = MENU_MAIN  # Kembali ke menu utama

        else:  # Jika game sedang berjalan
            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:  # Jika pengguna menutup jendela
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # Jika ESC ditekan
                        paused = True
                    elif event.key == K_j:  # Menembak dengan peluru 'J'
                        shoot_bullet('J')
                    elif event.key == K_k:  # Menembak dengan peluru 'K'
                        shoot_bullet('K')
                    elif event.key == K_l:  # Menembak dengan peluru 'L'
                        shoot_bullet('L')
                elif event.type == ADDENEMY:  # Menambahkan musuh baru
                    enemy_type = random.choice(['square', 'triangle', 'circle'])
                    if enemy_type == "square":
                        new_enemy = Enemy(RED, "square")
                    elif enemy_type == "triangle":
                        new_enemy = Enemy(GREEN, "triangle")
                    elif enemy_type == "circle":
                        new_enemy = Enemy(BLUE, "circle")
                    enemies.add(new_enemy)
                    all_sprites.add(new_enemy)

            # Update sprite dan logika permainan
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys)
            bullets.update()
            enemies.update()

            # Deteksi tabrakan peluru dan musuh
            for bullet in bullets:
                enemy_hit = pygame.sprite.spritecollideany(bullet, enemies)
                if enemy_hit:
                    if (bullet.color == enemy_hit.color) and (bullet.shape == enemy_hit.shape):
                        bullet.kill()
                        enemy_hit.kill()
                        score += 10
                        collision_sound.play()
                    else:
                        bullet.kill()

            # Deteksi tabrakan pemain dan musuh
            enemy_hit = pygame.sprite.spritecollideany(player, enemies)
            if enemy_hit:
                player.health -= 10
                enemy_hit.kill()
                if player.health <= 0:
                    reset_game()  # Reset game jika pemain kalah
                    current_menu = MENU_MAIN

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

    # Batasi frame rate
    clock.tick(60)

pygame.quit()
