import pygame
import math
import random

# --- BOSA UGUNSBUMBAS KLASE ---
class BossFireball:
    # funkcija __init__ pieņem int tipa vērtību x, int tipa vērtību y, int tipa vērtību target_x, int tipa vērtību target_y un atgriež None tipa vērtību None
    def __init__(self, x, y, target_x, target_y):
        self.pos = pygame.math.Vector2(x, y)
        direction = pygame.math.Vector2(target_x - x, target_y - y)
        
        # Normalizējam vektoru, lai ugunsbumba lidotu vienmērīgā ātrumā
        if direction.length() > 0:
            direction.normalize_ip()
            
        self.vel = direction * 4.5  # Ugunsbumbas lidošanas ātrums
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
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top": x, y = random.randint(0, screen_w), -100
        elif side == "bottom": x, y = random.randint(0, screen_w), screen_h + 100
        elif side == "left": x, y = -100, random.randint(0, screen_h)
        else: x, y = screen_w + 100, random.randint(0, screen_h)

        self.rect = pygame.Rect(x, y, 200, 200)  # Lielāks hitbox bosa attēlam
        self.wave = wave
        
        self.max_health = 20 + (1.5 * wave)
        self.health = self.max_health
        self.speed = min(5.0, 1.2 + (wave * 0.05))
        self.armor = wave // 3

        self.direction = "right"
        
        # --- UZBRUKUMA (ŠAUŠANAS) MAINĪGIE ---
        self.fireballs = []
        # Jo lielāks vilnis, jo mazāks gaidīšanas laiks starp šāvieniem!
        self.shoot_timer = max(50, 150 - (self.wave * 10)) 

        try:
            # Ielādējam un uzreiz mērogojam uz hitbox izmēru!
            self.original_image = pygame.image.load("photos/allOfBoss.png").convert_alpha()
            # Šeit mēs norādām 250x250, lai bilde precīzi iekļautos baltajā kvadrātā
            self.image = pygame.transform.scale(self.original_image, (350, 350))
        except:
            self.image = pygame.Surface((350, 350), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 0, 0), (0, 0, 350, 350))

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

        # Bosa attēla spoguļošana
        if hasattr(self, 'original_image'):
            if dx < 0 and self.direction != "left":
                self.image = pygame.transform.flip(pygame.transform.scale(self.original_image, (350, 350)), True, False)
                self.direction = "left"
            elif dx > 0 and self.direction != "right":
                self.image = pygame.transform.scale(self.original_image, (350, 350))
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

    # funkcija draw pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # 1. Vispirms uzzīmē visas ugunsbumbas (lai tās lidotu pirms/aiz bosa)
        for fireball in self.fireballs:
            fireball.draw(screen)

        # 2. Uzzīmē pašu bosu (using the new bigger image)
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)
        
        # 3. Uzzīmē HEALTH BAR virs bosa
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            bar_width = 200 # Platāka josla, lai izskatās labāk
            bar_x = self.rect.centerx - (bar_width // 2)
            bar_y = self.rect.y - 20
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 10))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, 10))




