import pygame
import math
import random

# Globālā kešatmiņa bosa animācijām — ielādē spritu loksni tikai VIENU REIZI
_BOSS_ANIMATIONS_CACHE = None

# Globālais saraksts, kurā tiek saglabātas ugunsbumbas pēc bosa nāves
# Tas ļauj ugunsbumbām palikt uz ekrāna pat pēc tam, kad boss ir nokauts
orphaned_fireballs = []

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
    # funkcija __init__ pieņem int tipa vērtību x, int tipa vērtību y, float tipa vērtību vel_x, float tipa vērtību vel_y un atgriež None tipa vērtību None
    def __init__(self, x, y, vel_x, vel_y, damage=70):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(vel_x, vel_y)
        self.radius = 12
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.damage = damage

    # funkcija update pieņem float tipa vērtību dilation un atgriež None tipa vērtību None
    def update(self, dilation):
        self.pos += self.vel * dilation
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    # funkcija draw pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # Uzzīmē mirdzošu ugunsbumbu (Sarkana ar dzeltenu vidu)
        pygame.draw.circle(screen, (255, 50, 0), self.rect.center, self.radius)
        pygame.draw.circle(screen, (255, 255, 0), self.rect.center, self.radius - 5)


# funkcija create_normal_fireball izveido standarta ugunsbumbu virzienā uz mērķi
def create_normal_fireball(x, y, target_x, target_y, boss_speed=1.2, damage=70):
    direction = pygame.math.Vector2(target_x - x, target_y - y)
    if direction.length() > 0:
        direction.normalize_ip()
    # [SAREŽĢĪTA LOĢIKA]: Ugunsbumbas ātrums skalējas ar bosa ātrumu, bet ne lineāri
    # Base speed 3.0 + boss_speed scaling, lai augstākos viļņos bosas šauj ātrākas lodes
    projectile_speed = 3.0 + boss_speed * 0.5
    return BossFireball(x, y, direction.x * projectile_speed, direction.y * projectile_speed, damage)


# funkcija create_circular_burst izveido ugunsbumbu riņķi ap bosa centru
def create_circular_burst(x, y, bullet_count=16, speed=3.5, damage=50):
    """
    [SAREŽĢĪTA LOĢIKA]: Speciālais cirkulārais uzbrukums.
    Izveido 'bullet_count' skaita ugunsbumbas vienādos leņķos ap bosu.
    Katrai lodes vel_x un vel_y tiek aprēķināti ar trigonometriju (cos/sin).
    """
    fireballs = []
    angle_step = 360.0 / bullet_count
    for i in range(bullet_count):
        angle_rad = math.radians(i * angle_step)
        vel_x = math.cos(angle_rad) * speed
        vel_y = math.sin(angle_rad) * speed
        fireballs.append(BossFireball(x, y, vel_x, vel_y, damage))
    return fireballs


class Boss:
    # funkcija __init__ pieņem int tipa vērtību screen_w, int tipa vērtību screen_h, int tipa vērtību wave un atgriež None tipa vērtību None
    def __init__(self, screen_w, screen_h, wave=1):
        global _BOSS_ANIMATIONS_CACHE

        self.screen_w = screen_w
        self.screen_h = screen_h

        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":      x, y = random.randint(0, screen_w), -100
        elif side == "bottom": x, y = random.randint(0, screen_w), screen_h + 100
        elif side == "left":   x, y = -100, random.randint(0, screen_h)
        else:                  x, y = screen_w + 100, random.randint(0, screen_h)

        self.rect = pygame.Rect(x, y, 170, 170)
        self.wave = wave

        # [SAREŽĢĪTA LOĢIKA]: Bosa HP skalēšana ar vilni.
        # Sākot no viļņa 1, bosa HP pieaug straujāk nekā parasto ienaidnieku HP,
        # lai augstākos viļņos boss būtu ievērojami grūtāks.
        # Parasta ienaidnieka HP ir 3 un tas nepieaug — boss aug eksponenciāli.
        self.max_health = 25 + (wave * 4.0) + (wave ** 1.5)
        self.health = self.max_health
        self.speed = min(5.0, 1.2 + (wave * 0.10))
        self.armor = wave // 3

        # --- ANIMĀCIJAS MAINĪGIE ---
        self.direction   = "down"
        self.frame_index = 0
        self.anim_timer  = 0
        self.anim_speed  = 0.12

        # --- PARASTO ŠĀVIENU TAIMERIS ---
        # Jo augstāks vilnis, jo mazāks gaidīšanas laiks starp šāvieniem
        self.fireballs   = []
        self.shoot_timer = max(50, 150 - (self.wave * 10))

        # --- SPECIĀLĀ UZBRUKUMA TAIMERIS (tikai no viļņa 10+) ---
        # [SAREŽĢĪTA LOĢIKA]: Speciālais uzbrukums aktivizējas ik pēc 10 sekundēm (600 kadri @ 60FPS).
        # Pirmais speciālais uzbrukums notiek pēc pilnām 10 sekundēm, ne uzreiz.
        self.special_timer    = 600
        self.special_cooldown = 600  # 10 sekundes @ 60 FPS
        self.special_active   = False  # True kamēr notiek speciālā uzbrukuma animācija
        self.special_anim_timer = 0    # Cik ilgi ir aktīvs speciālais uzbrukums (vizuālam efektam)

        # --- SPRITU LOKSNES IELĀDE AR KEŠATMIŅU ---
        # [SAREŽĢĪTA LOĢIKA]: Spritu loksnes ielāde ar kešatmiņu (Cache).
        # Bilde tiek ielādēta un sagriezta tikai VIENU REIZI — pārējie bosi izmanto kešu.
        # Tas novērš lag spikes, kad parādās jauns boss.
        if _BOSS_ANIMATIONS_CACHE is None:
            _BOSS_ANIMATIONS_CACHE = {"up": [], "down": [], "left": [], "right": []}
            try:
                sheet = pygame.image.load("photos/allOfBoss.png").convert_alpha()

                frame_w   = 125
                frame_h   = 157
                start_x   = 10
                start_y   = 80
                padding_x = 26
                padding_y = 3
                num_frames = 2
                scale = (150, 150)

                for i in range(num_frames):
                    _BOSS_ANIMATIONS_CACHE["up"].append(
                        get_image_from_sheet(sheet, i, 0, frame_w, frame_h,
                                             start_x, start_y, padding_x, padding_y, scale))
                    _BOSS_ANIMATIONS_CACHE["down"].append(
                        get_image_from_sheet(sheet, i, 1, frame_w, frame_h,
                                             start_x, start_y, padding_x, padding_y, scale))

                    img_right = get_image_from_sheet(sheet, i, 2, frame_w, frame_h,
                                                     start_x, start_y, padding_x, padding_y, scale)
                    _BOSS_ANIMATIONS_CACHE["right"].append(img_right)
                    _BOSS_ANIMATIONS_CACHE["left"].append(
                        pygame.transform.flip(img_right, True, False))

            except Exception as _e:
                surf = pygame.Surface((350, 350), pygame.SRCALPHA)
                pygame.draw.rect(surf, (200, 0, 0), (0, 0, 350, 350))
                _BOSS_ANIMATIONS_CACHE = {
                    "up":    [surf],
                    "down":  [surf],
                    "left":  [surf],
                    "right": [surf],
                }

        self.animations = _BOSS_ANIMATIONS_CACHE
        self.image = self.animations["down"][0]

    # funkcija _is_fireball_out_of_bounds pārbauda, vai ugunsbumba ir pārāk tālu ārpus ekrāna
    def _is_fireball_out_of_bounds(self, fb):
        margin = 400
        return (fb.pos.x < -margin or fb.pos.x > self.screen_w + margin or
                fb.pos.y < -margin or fb.pos.y > self.screen_h + margin)

    # funkcija update pieņem pygame.Rect tipa vērtību player_rect, float tipa vērtību dilation un atgriež int tipa vērtību damage_dealt_to_player
    def update(self, player_rect, dilation):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # 1. Bosa kustība
        if dist > 0:
            self.rect.x += int((dx / dist) * self.speed * dilation)
            self.rect.y += int((dy / dist) * self.speed * dilation)

            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

            frames = self.animations[self.direction]
            if frames:
                self.anim_timer += self.anim_speed * dilation
                if self.anim_timer >= len(frames):
                    self.anim_timer = 0
                self.frame_index = int(self.anim_timer)
                self.image = frames[self.frame_index]

        # 2. Parasto šāvienu loģika
        damage_dealt_to_player = 0

        self.shoot_timer -= dilation
        if self.shoot_timer <= 0:
            self.fireballs.append(
                create_normal_fireball(
                    self.rect.centerx, self.rect.centery,
                    player_rect.centerx, player_rect.centery,
                    self.speed
                )
            )
            self.shoot_timer = max(50, 150 - (self.wave * 10))

        # [SAREŽĢĪTA LOĢIKA]: Speciālais cirkulārais uzbrukums.
        # Aktivizējas tikai sākot no viļņa 10. Katras 10 sekundes boss izšauj lodes
        # visās virzienos riņķī. Lodes skaits pieaug ar katru vilni (vismaz 12, vairāk augstākos viļņos).
        if self.wave >= 10:
            self.special_timer -= dilation
            if self.special_timer <= 0:
                bullet_count = min(32, 12 + (self.wave - 10) // 2)
                burst_speed  = 3.0 + (self.wave - 10) * 0.05
                burst_fireballs = create_circular_burst(
                    self.rect.centerx, self.rect.centery,
                    bullet_count=bullet_count,
                    speed=burst_speed,
                    damage=50
                )
                self.fireballs.extend(burst_fireballs)
                self.special_timer     = self.special_cooldown
                # Ieslēdzam īsu vizuālo efektu (flash uz ekrāna), kas ilgst 20 kadrus
                self.special_active    = True
                self.special_anim_timer = 20

        # Speciālā uzbrukuma vizuālā efekta taimeris
        if self.special_active:
            self.special_anim_timer -= dilation
            if self.special_anim_timer <= 0:
                self.special_active = False

        # 3. Visu ugunsbumbu atjaunināšana un sadursmes pārbaude
        to_remove = []
        for fb in self.fireballs:
            fb.update(dilation)
            if fb.rect.colliderect(player_rect):
                damage_dealt_to_player += fb.damage
                to_remove.append(fb)
            elif self._is_fireball_out_of_bounds(fb):
                to_remove.append(fb)

        # [SAREŽĢĪTA LOĢIKA]: Efektīva ugunsbumbu dzēšana.
        # Veidojam jaunu sarakstu, nevis dzēšam ciklā (tas novērš index kļūdas un ir ātrāks).
        if to_remove:
            remove_set = set(id(fb) for fb in to_remove)
            self.fireballs = [fb for fb in self.fireballs if id(fb) not in remove_set]

        return damage_dealt_to_player

    # funkcija release_fireballs pārvieto visas aktīvās ugunsbumbas uz globālo sarakstu, lai tās paliktu uz ekrāna pēc bosa nāves
    def release_fireballs(self):
        """
        [SAREŽĢĪTA LOĢIKA]: Bosa nāves ugunsbumbu saglabāšana.
        Pārvietojam VISAS boss ugunsbumbas uz 'orphaned_fireballs' sarakstu.
        Tādejādi, pat pēc tam, kad boss tiek noņemts no 'bosses' saraksta,
        visas lidojošās lodes turpina pastāvēt un kaitēt spēlētājam.
        """
        orphaned_fireballs.extend(self.fireballs)
        self.fireballs.clear()

    # funkcija draw pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # 1. Uzzīmē visas ugunsbumbas
        for fireball in self.fireballs:
            fireball.draw(screen)

        # 2. Speciālā uzbrukuma vizuālais efekts — mirgojoša aura ap bosu
        if self.special_active:
            # Efekts: pulsējoša oranža/balta aura, kuras intensitāte samazinās ar laiku
            aura_alpha = int(200 * (self.special_anim_timer / 20))
            aura_radius = 100 + int((1 - self.special_anim_timer / 20) * 60)
            aura_surf = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 140, 0, aura_alpha), (aura_radius, aura_radius), aura_radius)
            screen.blit(aura_surf, aura_surf.get_rect(center=self.rect.center))

        # 3. Uzzīmē pašu bosu
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)

        # 4. Uzzīmē HEALTH BAR virs bosa
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            bar_width = 200
            bar_x = self.rect.centerx - (bar_width // 2)
            bar_y = self.rect.y - 20
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 10))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * health_ratio), 10))


# funkcija update_orphaned_fireballs atjaunina un zīmē ugunsbumbas, kuras ir palikušas pēc bosa nāves
def update_orphaned_fireballs(screen, player_rect, dilation, screen_w, screen_h):
    """
    [SAREŽĢĪTA LOĢIKA]: 'Bezīpašnieka' ugunsbumbu sistēma.
    Šo funkciju izsauc main.py katru kadru, lai atjauninātu un attēlotu
    ugunsbumbas, kuras turpina lidot pat pēc bosa nāves.
    Atgriež kopējo bojājumu skaitu, ko šīs lodes nodarījušas spēlētājam.
    """
    if not orphaned_fireballs:
        return 0

    damage_total = 0
    margin = 400
    to_remove = []

    for fb in orphaned_fireballs:
        fb.update(dilation)
        fb.draw(screen)
        if fb.rect.colliderect(player_rect):
            damage_total += fb.damage
            to_remove.append(fb)
        elif (fb.pos.x < -margin or fb.pos.x > screen_w + margin or
              fb.pos.y < -margin or fb.pos.y > screen_h + margin):
            to_remove.append(fb)

    if to_remove:
        remove_set = set(id(fb) for fb in to_remove)
        # Dzēšam nolidojušās vai trāpījušās lodes no globālā saraksta
        orphaned_fireballs[:] = [fb for fb in orphaned_fireballs if id(fb) not in remove_set]

    return damage_total