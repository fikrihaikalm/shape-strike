import pygame
import random
from pygame.locals import *
import os
import math

#Inisialisasi pygame
pygame.init()

#Ukuran layar
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#Warna
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
SEMI_BLACK = (0, 0, 0, 150)  

#Variabel game
running = True
paused = False
score = 0
level = 1
shake_duration = 0
shake_offset = (0, 0)

#Kapal yang tersedia
ship_options = [
    "ship1.png",
    "ship2.png",
    "ship3.png"
]
selected_ship = ship_options[0]  #Kapal default


#Sound effects
shoot_sound = pygame.mixer.Sound("shoot.wav")
collision_sound = pygame.mixer.Sound("collision.wav")

#Musik
menu_music = "dust.mp3" 
game_music = "game_music.mp3"
pygame.mixer.music.set_volume(0.5)  #Atur volume musik

#Fungsi untuk memuat highscore dari file
def load_highscore():
    if not os.path.exists("highscore.txt"):
        with open("highscore.txt", "w") as file:
            file.write("0")
    
    #Baca nilai highscore dari file
    with open("highscore.txt", "r") as file:
        highscore = int(file.read())  #Ubah isi file menjadi integer
    return highscore

#Fungsi untuk menyimpan highscore ke file
def save_highscore(new_highscore):
    with open("highscore.txt", "w") as file:
        file.write(str(new_highscore))

def check_highscore(score, highscore):
    if score > highscore:
        save_highscore(score)
        highscore = score
    return highscore

highscore = load_highscore()


def play_music(menu=True):
    """Memutar musik sesuai dengan menu saat ini."""
    if menu:
        pygame.mixer.music.load(menu_music )
        pygame.mixer.music.play(-1, 0.0)  #Putar musik menu secara berulang
    else:
        pygame.mixer.music.load(game_music )
        pygame.mixer.music.play(-1, 0.0)  #Putar musik game secara berulang

def stop_music():
    """Menghentikan musik yang sedang diputar."""
    pygame.mixer.music.stop()


#Background
BGspace = pygame.image.load("bg.jpg")
BGspace = pygame.transform.scale(BGspace, (SCREEN_WIDTH, SCREEN_HEIGHT))

#Player
class Player(pygame.sprite.Sprite):
    def __init__(self, selected_ship):
        super().__init__()
        self.image = pygame.image.load(selected_ship).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Sesuaikan ukuran
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.health = 100
        self.speed = 12

    def update(self, pressed_keys=None):
        #Variabel untuk kecepatan pada masing-masing sumbu
        move_x = 0
        move_y = 0

        if pressed_keys:
            if pressed_keys[K_a]:
                move_x = -self.speed
            if pressed_keys[K_d]:
                move_x = self.speed
            if pressed_keys[K_w]:
                move_y = -self.speed
            if pressed_keys[K_s]:
                move_y = self.speed

        #Hitung panjang vektor gerakan dan normalisasi
        move_length = math.sqrt(move_x ** 2 + move_y ** 2)
        if move_length != 0:  #Jika ada gerakan
            #Normalisasi vektor dan kalikan dengan kecepatan standar
            move_x = (move_x / move_length) * self.speed
            move_y = (move_y / move_length) * self.speed

        #Update posisi dengan kecepatan yang sudah dinormalisasi
        self.rect.move_ip(move_x, move_y)

        #Batasi gerakan pemain dalam layar
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

#Peluru
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

#Musuh
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
            global score
            score -= 10 

#Efek Screen Shake
def screen_shake():
    global shake_duration, shake_offset
    if shake_duration > 0:
        shake_offset = (random.randint(-5, 5), random.randint(-5, 5))
        shake_duration -= 1
    else:
        shake_offset = (0, 0)

#Fungsi menembak
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

#Setup sprite
player = Player(selected_ship)
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
all_sprites.add(player)

#Clock
clock = pygame.time.Clock()

#Spawning musuh dengan berbagai tipe
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 1000)


#Menu states
MENU_MAIN = 0
MENU_PLAY = 1
MENU_SHIP_SELECTION = 2
MENU_PAUSE = 3
current_menu = MENU_MAIN


#Menu utama
def draw_main_menu():
    screen.blit(BGspace, (0, 0))
    font = pygame.font.Font(None, 50)
    start_text = font.render("Start", True, WHITE)
    select_ship_text = font.render("Pilih Kapal", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)

    screen.blit(start_text, (SCREEN_WIDTH // 2 - 50, 200))
    screen.blit(select_ship_text, (SCREEN_WIDTH // 2 - 85, 300))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - 50, 400))
    pygame.display.flip()

def main_menu_logic():
    global current_menu, running
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 250:  #Start
                stop_music()  #Hentikan musik menu utama
                play_music(False)  #Mainkan musik game
                current_menu = MENU_PLAY
            elif 300 < y < 350:  #Pilih Kapal
                current_menu = MENU_SHIP_SELECTION
            elif 400 < y < 450:  #Exit
                running = False

#Memutar musik di menu utama
if current_menu == MENU_MAIN:  #Menu Utama
    play_music(True)  #Memutar musik menu
    draw_main_menu()  #Gambar menu utama
    main_menu_logic()  #Tangani logika menu utama

#Memutar musik dalam permainan
elif current_menu == MENU_PLAY:  #Game Dimulai
    if not paused:  #Jika game dalam keadaan tidak pause
        play_music(False)  #Memutar musik game
    else:  #Ketika game dijeda
        stop_music()  #Hentikan musik

def draw_pause_menu():
    screen.blit(BGspace, (0, 0))
    font = pygame.font.Font(None, 50)
    continue_text = font.render("Lanjut", True, WHITE)
    exit_text = font.render("Keluar", True, WHITE)

    screen.blit(continue_text, (SCREEN_WIDTH // 2 - 50, 200))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - 50, 300))

    pygame.display.flip()

def draw_ship_selection():
    screen.blit(BGspace, (0, 0))

    font = pygame.font.Font(None, 50)
    text = font.render("Pilih Kapal", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, 50))

    #Tampilkan opsi kapal
    for i, ship in enumerate(ship_options):
        ship_image = pygame.image.load(ship).convert_alpha()
        ship_image = pygame.transform.scale(ship_image, (100, 100))
        screen.blit(ship_image, (150 + i * 150, 200))
    
    #Tampilkan opsi kapal custom jika ada
    if custom_ship:
        custom_image = pygame.image.load(custom_ship).convert_alpha()
        custom_image = pygame.transform.scale(custom_image, (100, 100))
        screen.blit(custom_image, (600, 200))

    pygame.display.flip()

def load_custom_ship():
    global custom_ship
    custom_ship = "custom_ship.png"  #Asumsikan file diletakkan manual
    ship_options.append(custom_ship)

def pause_menu_logic():
    global current_menu, running, paused, highscore, score
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 200 < y < 250:  #Lanjut
                paused = False
                current_menu = MENU_PLAY
            elif 300 < y < 350:  #Keluar
                #Update highscore sebelum keluar
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)

                #Reset game state tanpa keluar aplikasi
                paused = False
                reset_game()  #Mengatur ulang game
                current_menu = MENU_MAIN  #Kembali ke menu utama

def ship_selection_logic():
    global current_menu, selected_ship, player  #Tambahkan player ke variabel global
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            if 150 < x < 250 and 200 < y < 300:  #Pilih kapal pertama
                selected_ship = ship_options[0]
            elif 300 < x < 400 and 200 < y < 300:  #Pilih kapal kedua
                selected_ship = ship_options[1]
            elif 450 < x < 550 and 200 < y < 300:  #Pilih kapal ketiga
                selected_ship = ship_options[2]
            elif custom_ship and 600 < x < 700 and 200 < y < 300:  #Pilih kapal custom
                selected_ship = custom_ship

            #Perbarui sprite pemain setelah kapal dipilih
            all_sprites.remove(player)  #Hapus player lama
            player = Player(selected_ship)  #Buat player baru dengan kapal baru
            all_sprites.add(player)  #Tambahkan player baru ke grup sprite

            current_menu = MENU_MAIN  #Kembali ke menu utama

def reset_game():
    """Mengatur ulang variabel dan sprite ke kondisi awal."""
    global player, all_sprites, enemies, bullets, score

    #Reset variabel game
    score = 0
    paused = False

    #Hapus semua sprite
    all_sprites.empty()
    enemies.empty()
    bullets.empty()

    # Buat ulang pemain dengan gambar kapal yang dipilih
    player = Player(selected_ship)
    all_sprites.add(player)

while running:
    if current_menu == MENU_MAIN:  #Menu Utama
        draw_main_menu()  #Gambar menu utama
        main_menu_logic()  #Tangani logika menu utama

    elif current_menu == MENU_SHIP_SELECTION:  # Menu Pilih Kapal
        draw_ship_selection()  #Gambar menu pilih kapal
        ship_selection_logic()  #Tangani logika menu pilih kapal

    elif current_menu == MENU_PLAY:  #Game Dimulai
        if paused:  # ika game dalam keadaan pause
            draw_pause_menu()  #Gambar menu pause
            option = pause_menu_logic()  #Tangani input dari menu pause
            
            if option == "resume":  #Lanjutkan permainan
                paused = False
            elif option == "quit":  #Reset game dan kembali ke menu utama
                reset_game() 
                current_menu = MENU_MAIN  #Kembali ke menu utama

        else:  #Jika game sedang berjalan
            #Event handling
            for event in pygame.event.get():
                if event.type == QUIT:  #Jika pengguna menutup jendela
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  #Jika ESC ditekan
                        paused = True
                    elif event.key == K_j:  #Menembak dengan peluru 'J'
                        shoot_bullet('J')
                    elif event.key == K_k:  #Menembak dengan peluru 'K'
                        shoot_bullet('K')
                    elif event.key == K_l:  #Menembak dengan peluru 'L'
                        shoot_bullet('L')
                elif event.type == ADDENEMY:  #Menambahkan musuh baru
                    enemy_type = random.choice(['square', 'triangle', 'circle'])
                    if enemy_type == "square":
                        new_enemy = Enemy(RED, "square")
                    elif enemy_type == "triangle":
                        new_enemy = Enemy(GREEN, "triangle")
                    elif enemy_type == "circle":
                        new_enemy = Enemy(BLUE, "circle")
                    enemies.add(new_enemy)
                    all_sprites.add(new_enemy)

            #Update sprite dan logika permainan
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys)
            bullets.update()
            enemies.update()

            # eteksi tabrakan peluru dan musuh
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
                    if score > highscore:
                        highscore = score
                        save_highscore(highscore)  #Simpan highscore ke file
                                
                    reset_game()  #Reset game jika pemain kalah
                    current_menu = MENU_MAIN
            
            for enemy in enemies:
                if enemy.rect.top > SCREEN_HEIGHT:
                    enemy.kill()
                    score -= 10 

            #Gambar latar belakang dan sprite
            screen.blit(BGspace, (0, 0))
            all_sprites.draw(screen)
            player.draw_health_bar(screen)

            #Tampilkan skor
            font = pygame.font.Font(None, 36)
            text = font.render("Score: " + str(score), True, WHITE)
            screen.blit(text, (10, 10))
            
            highscore_text = font.render("Highscore: " + str(highscore), True, WHITE)
            screen.blit(highscore_text, (10, 50))  #Posisi di bawah score

            #Update layar
            pygame.display.flip()

    #Batasi frame rate
    clock.tick(30)

highscore = check_highscore(score, highscore)

pygame.quit()
