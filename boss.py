import pygame
import math
import random

# Globālā kešatmiņa bosa animācijām — ielādē spritu loksni tikai VIENU REIZI
_BOSS_ANIMATIONS_CACHE = None

# funkcija get_image_from_sheet pieņem pygame.Surface tipa vērtību sheet un atgriež pygame.Surface tipa vērtību image
def get_image_from_sheet(sheet, column, row, width, height, start_x=0, start_y=0, padding_x=0, padding_y=0, scale_size=(150, 150)):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    exact_x = start_x + (column * width) + (column * padding_x)
    exact_y = start_y + (row * height) + (row * padding_y)
    crop_rect = pygame.Rect(exact_x, exact_y, width, height)
    image.blit(sheet, (0, 0), crop_rect)
    return pygame.transform.scale(image, scale_size)


# --- BOSA UGUNSBUMBAS KLASE ---
class BossFireball:
    # funkcija __init__ pieņem int tipa vērtību x, int tipa vērtību y, int tipa vērtību target_x, int tipa vērtību target_y, float tipa vērtību boss_speed un atgriež None tipa vērtību None
    def __init__(self, x, y, target_x, target_y, boss_speed=1.2):
        self.pos = pygame.math.Vector2(x, y)
        direction = pygame.math.Vector2(target_x - x, target_y - y)
        
        # Normalizējam vektoru, lai ugunsbumba lidotu vienmērīgā ātrumā
        if direction.length() > 0:
            direction.normalize_ip()
        
        # Ugunsbumbas ātrums skalējas ar bosa ātrumu, bet ne lineāri
        # Base speed 3.0 + boss_speed scaling
        projectile_speed = 3.0 + boss_speed * 0.5
        self.vel = direction * projectile_speed
        self.radius = 12
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        
    # funkcija update pieņem float tipa vērtību dilation un atgriež None tipa vērtību None
    def update(self, dilation):
        self.pos += self.vel * dilation
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    # funkcija draw pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # Uzzīmē mirdzošu ugunsbumbu (Sarkana ar dzeltenu vidu)
        pygame.draw.circle(screen, (255, 50, 0), self.rect.center, self.radius)
        pygame.draw.circle(screen, (255, 255, 0), self.rect.center, self.radius - 5)


class Boss:
    # funkcija __init__ pieņem int tipa vērtību screen_w, int tipa vērtību screen_h, int tipa vērtību wave un atgriež None tipa vērtību None
    def __init__(self, screen_w, screen_h, wave=1):
        global _BOSS_ANIMATIONS_CACHE

        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":    x, y = random.randint(0, screen_w), -100
        elif side == "bottom": x, y = random.randint(0, screen_w), screen_h + 100
        elif side == "left": x, y = -100, random.randint(0, screen_h)
        else:                x, y = screen_w + 100, random.randint(0, screen_h)

        self.rect = pygame.Rect(x, y, 350, 350)  # Lielāks hitbox bosa attēlam
        self.wave = wave

        self.max_health = 25 + (1.5 * wave)
        self.health = self.max_health
        self.speed = min(5.0, 1.2 + (wave * 0.10))  # Bosa ātrums skalējas ar vilni, bet ne lineāri
        self.armor = wave // 3

        # --- ANIMĀCIJAS MAINĪGIE (tāpat kā enemy.py) ---
        self.direction  = "down"
        self.frame_index = 0
        self.anim_timer  = 0
        self.anim_speed  = 0.12   # nedaudz lēnāks par ienaidnieku — boss ir masīvāks

        # --- UZBRUKUMA (ŠAUŠANAS) MAINĪGIE ---
        self.fireballs  = []
        # Jo lielāks vilnis, jo mazāks gaidīšanas laiks starp šāvieniem!
        self.shoot_timer = max(50, 150 - (self.wave * 10))

        # [SAREŽĢĪTA LOĢIKA]: Spritu loksnes ielāde ar kešatmiņu (Cache)
        # Bilde tiek ielādēta un sagriezta tikai VIENU REIZI — pārējie bosi izmanto kešu.
        if _BOSS_ANIMATIONS_CACHE is None:
            _BOSS_ANIMATIONS_CACHE = {"up": [], "down": [], "left": [], "right": []}
            try:
                sheet = pygame.image.load("photos/allOfBoss.png").convert_alpha()

                # ── Pielāgo šos skaitļus savam spritu lapas izkārtojumam ──
                frame_w = 125    # Width of the box
                frame_h = 157       # Height of the box
                start_x = 10   # Distance from left edge to the first box
                start_y = 80    # Distance from top edge to the first box
                padding_x = 26     # Empty space between columns
                padding_y = 3    # Empty space between rows
                num_frames = 2     # Number of columns

                scale = (150, 150)  # Galīgais izmērs, uz kuru scale katru kadru

                for i in range(num_frames):
                    # Rinda 0: Uz augšu (skatās prom)
                    _BOSS_ANIMATIONS_CACHE["up"].append(
                        get_image_from_sheet(sheet, i, 0, frame_w, frame_h,
                                             start_x, start_y, padding_x, padding_y, scale))
                    # Rinda 1: Uz leju (skatās uz mums)
                    _BOSS_ANIMATIONS_CACHE["down"].append(
                        get_image_from_sheet(sheet, i, 1, frame_w, frame_h,
                                             start_x, start_y, padding_x, padding_y, scale))

                    # Rinda 2: 
                    img_right = get_image_from_sheet(sheet, i, 2, frame_w, frame_h,
                                                     start_x, start_y, padding_x, padding_y, scale)
                    _BOSS_ANIMATIONS_CACHE["right"].append(img_right)

                    # Apgriežam "pa labi" bildi, lai iegūtu "pa kreisi"
                    _BOSS_ANIMATIONS_CACHE["left"].append(
                        pygame.transform.flip(img_right, True, False))

            except Exception as _e:
                # Ja bildi neatrod — rāda sarkanu kvadrātu kā rezerves variantu
                surf = pygame.Surface((350, 350), pygame.SRCALPHA)
                pygame.draw.rect(surf, (200, 0, 0), (0, 0, 350, 350))
                _BOSS_ANIMATIONS_CACHE = {
                    "up":    [surf],
                    "down":  [surf],
                    "left":  [surf],
                    "right": [surf],
                }

        # Piešķiram bosam jau ielādēto animāciju vārdnīcu no globālās atmiņas
        self.animations = _BOSS_ANIMATIONS_CACHE
        self.image = self.animations["down"][0]

    # funkcija update pieņem pygame.Rect tipa vērtību player_rect, float tipa vērtību dilation un atgriež int tipa vērtību damage_dealt_to_player
    def update(self, player_rect, dilation):
        # Aprēķina attāluma vektoru no bosa uz spēlētāju (horizontāli un vertikāli)
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # 1. Bosa kustība
        if dist > 0:
            self.rect.x += (dx / dist) * self.speed * dilation
            self.rect.y += (dy / dist) * self.speed * dilation

            # Nosakām virzienu tāpat kā enemy.py — pēc dominējošās ass
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

            # Animācijas kadra virzīšana uz priekšu
            frames = self.animations[self.direction]
            if len(frames) > 0:
                self.anim_timer += self.anim_speed * dilation
                if self.anim_timer >= len(frames):
                    self.anim_timer = 0
                self.frame_index = int(self.anim_timer)
                self.image = frames[self.frame_index]

        # 2. [SAREŽĢĪTA LOĢIKA]: Ugunsbumbu šaušana
        damage_dealt_to_player = 0

        self.shoot_timer -= 1 * dilation
        if self.shoot_timer <= 0:
            # Izšauj ugunsbumbu spēlētāja virzienā, padodot bosa ātrumu!
            self.fireballs.append(BossFireball(
                self.rect.centerx, self.rect.centery,
                player_rect.centerx, player_rect.centery,
                self.speed))
            # Atiestata taimeri (viļņos ar augstu numuru šaus ļoti bieži)
            self.shoot_timer = max(50, 150 - (self.wave * 10))

        # Atjaunina visas lidojošās ugunsbumbas
        for fb in self.fireballs[:]:
            fb.update(dilation)
            # Pārbauda, vai trāpīja spēlētājam
            if fb.rect.colliderect(player_rect):
                damage_dealt_to_player += 70  # Katra ugunsbumba nodara 70 saapes/damage!
                self.fireballs.remove(fb)
            # Iznīcina ugunsbumbu, ja tā aizlido pārāk tālu no bosa (1500 pikseļi)
            elif fb.pos.distance_to(pygame.math.Vector2(self.rect.center)) > 1500:
                self.fireballs.remove(fb)

        # Mēs atgriežam bojājumu skaitu, lai main.py varētu atņemt spēlētāja dzīvību
        return damage_dealt_to_player

    # funkcija draw pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # 1. Vispirms uzzīmē visas ugunsbumbas (lai tās lidotu pirms/aiz bosa)
        for fireball in self.fireballs:
            fireball.draw(screen)

        # 2. Uzzīmē pašu bosu ar aktuālo animācijas kadru
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)

        # 3. Uzzīmē HEALTH BAR virs bosa
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            bar_width = 200  # Platāka josla, lai izskatās labāk
            bar_x = self.rect.centerx - (bar_width // 2)
            bar_y = self.rect.y - 20
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 10))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, 10))