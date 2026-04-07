import pygame
import math
import random

# --- BOSA UGUNSBUMBAS KLASE ---
class BossFireball:
    def __init__(self, x, y, target_x, target_y):
        self.pos = pygame.math.Vector2(x, y)
        direction = pygame.math.Vector2(target_x - x, target_y - y)
        
        # Normalizējam vektoru, lai ugunsbumba lidotu vienmērīgā ātrumā
        if direction.length() > 0:
            direction.normalize_ip()
            
        self.vel = direction * 4.5  # Ugunsbumbas lidošanas ātrums
        self.radius = 12
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        
    def update(self, dilation):
        self.pos += self.vel * dilation
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    def draw(self, screen):
        # Uzzīmē mirdzošu ugunsbumbu (Sarkana ar dzeltenu vidu)
        pygame.draw.circle(screen, (255, 50, 0), self.rect.center, self.radius)
        pygame.draw.circle(screen, (255, 255, 0), self.rect.center, self.radius - 5)


class Boss:
    def __init__(self, screen_w, screen_h, wave=1):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top": x, y = random.randint(0, screen_w), -100
        elif side == "bottom": x, y = random.randint(0, screen_w), screen_h + 100
        elif side == "left": x, y = -100, random.randint(0, screen_h)
        else: x, y = screen_w + 100, random.randint(0, screen_h)

        self.rect = pygame.Rect(x, y, 100, 100) 
        self.wave = wave
        
        self.max_health = 10 + (0.5 * wave)
        self.health = self.max_health
        self.speed = min(3.0, 1.2 + (wave * 0.05))
        self.armor = wave // 3

        self.direction = "right"
        
        # --- UZBRUKUMA (ŠAUŠANAS) MAINĪGIE ---
        self.fireballs = []
        # Jo lielāks vilnis, jo mazāks gaidīšanas laiks starp šāvieniem!
        self.shoot_timer = max(50, 150 - (self.wave * 10)) 

        try:
            self.original_image = pygame.image.load("photos/allOfBoss.png").convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (120, 120))
        except:
            self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 0, 0), (0, 0, 100, 100))

    def update(self, player_rect, dilation):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # 1. Bosa kustība
        if dist > 0:
            self.rect.x += (dx / dist) * self.speed * dilation
            self.rect.y += (dy / dist) * self.speed * dilation

        # Bosa attēla spoguļošana
        if hasattr(self, 'original_image'):
            if dx < 0 and self.direction != "left":
                self.image = pygame.transform.flip(pygame.transform.scale(self.original_image, (120, 120)), True, False)
                self.direction = "left"
            elif dx > 0 and self.direction != "right":
                self.image = pygame.transform.scale(self.original_image, (120, 120))
                self.direction = "right"

        # 2. [SAREŽĢĪTA LOĢIKA]: Ugunsbumbu šaušana
        damage_dealt_to_player = 0
        
        self.shoot_timer -= 1 * dilation
        if self.shoot_timer <= 0:
            # Izšauj ugunsbumbu spēlētāja virzienā!
            self.fireballs.append(BossFireball(self.rect.centerx, self.rect.centery, player_rect.centerx, player_rect.centery))
            # Atiestata taimeri (viļņos ar augstu numuru šaus ļoti bieži)
            self.shoot_timer = max(50, 150 - (self.wave * 10))

        # Atjaunina visas lidojošās ugunsbumbas
        for fb in self.fireballs[:]:
            fb.update(dilation)
            # Pārbauda, vai trāpīja spēlētājam
            if fb.rect.colliderect(player_rect):
                damage_dealt_to_player += 70  # Katra ugunsbumba nodara 20 saapes/damage!
                self.fireballs.remove(fb)
            # Iznīcina ugunsbumbu, ja tā aizlido pārāk tālu no bosa (1500 pikseļi)
            elif fb.pos.distance_to(pygame.math.Vector2(self.rect.center)) > 1500:
                self.fireballs.remove(fb)

        # Mēs atgriežam bojājumu skaitu, lai main.py varētu atņemt spēlētāja dzīvību
        return damage_dealt_to_player

    def draw(self, screen):
        # 1. Vispirms uzzīmē visas ugunsbumbas (lai tās lidotu pirms/aiz bosa)
        for fb in self.fireballs:
            fb.draw(screen)
            
        # 2. Uzzīmē pašu bosu
        new_size = (self.image.get_width() * 3, self.image.get_height() * 3)
        bigger_image = pygame.transform.scale(self.image, new_size)

        # 2. Uzzīmē pašu bosu (using the new bigger image)
        draw_rect = bigger_image.get_rect(center=self.rect.center)
        screen.blit(bigger_image, draw_rect)
        
        # 3. Uzzīmē dzīvības joslu
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            bar_width = 80
            bar_x = self.rect.centerx - (bar_width // 2)
            bar_y = self.rect.y - 15
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 6))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, 6))