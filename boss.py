import pygame
import math
import random

class Boss:
    # funkcija __init__ pieņem Boss tipa vērtību self, int tipa vērtību screen_w un int tipa vērtību screen_h un atgriež None tipa vērtību None
    def __init__(self, screen_w, screen_h):
        # [SAREŽĢĪTA LOĢIKA]: Nejauša parādīšanās vieta ārpus ekrāna
        # Boss neparādās ekrāna vidū, bet gan aiz kādas no 4 ekrāna malām (augšas, apakšas, kreisās vai labās),
        # lai spēlētājs redzētu, kā viņš episki ienāk arēnā.
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x, y = random.randint(0, screen_w), -100
        elif side == "bottom":
            x, y = random.randint(0, screen_w), screen_h + 100
        elif side == "left":
            x, y = -100, random.randint(0, screen_h)
        else:
            x, y = screen_w + 100, random.randint(0, screen_h)

        self.rect = pygame.Rect(x, y, 100, 100) # Lielāks hitbox nekā parastiem ienaidniekiem
        self.max_health = 500
        self.health = 500
        self.speed = 1.5
        self.armor = 2

        self.direction = "right" # Sākotnējais virziens

        # [SAREŽĢĪTA LOĢIKA]: Attēla ielāde un izmēra pielāgošana
        try:
            # Ielādējam oriģinālo attēlu un saglabājam to 'self.original_image',
            # lai vēlāk to varētu spoguļot bez kvalitātes zuduma.
            self.original_image = pygame.image.load("photos/allOfBoss.png").convert_alpha()
            # Bosa attēlu mērogojam lielāku (120x120 pikseļi)
            self.image = pygame.transform.scale(self.original_image, (120, 120))
        except:
            # Rezerves variants, ja 'boss.png' nav atrasts (sarkans kvadrāts)
            self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 0, 0), (0, 0, 100, 100))

    # funkcija update pieņem Boss tipa vērtību self, pygame.Rect tipa vērtību player_rect un float tipa vērtību dilation un atgriež None tipa vērtību None
    def update(self, player_rect, dilation):
        # Aprēķina X un Y distanci starp priekšnieku un spēlētāju
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # Kustības loģika (Tāpat kā parastiem ienaidniekiem)
        if dist > 0:
            self.rect.x += (dx / dist) * self.speed * dilation
            self.rect.y += (dy / dist) * self.speed * dilation

        # [SAREŽĢĪTA LOĢIKA]: Bosa attēla spoguļošana
        # Ja priekšniekam ir ielādēts attēls, mēs to pagriežam pa kreisi vai pa labi
        # atkarībā no tā, kurā virzienā atrodas spēlētājs.
        if hasattr(self, 'original_image'):
            if dx < 0 and self.direction != "left":
                # Spēlētājs ir pa kreisi - spoguļojam attēlu horizontāli (True, False)
                self.image = pygame.transform.flip(pygame.transform.scale(self.original_image, (120, 120)), True, False)
                self.direction = "left"
            elif dx > 0 and self.direction != "right":
                # Spēlētājs ir pa labi - izmantojam oriģinālo attēlu
                self.image = pygame.transform.scale(self.original_image, (120, 120))
                self.direction = "right"

    # funkcija draw pieņem Boss tipa vērtību self un pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # Uzzīmē bosa attēlu ekrānā, iecentrētu pret viņa hitbox
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)
        
        # [SAREŽĢĪTA LOĢIKA]: Priekšnieka dzīvības josla (Boss Health Bar)
        # Šī dzīvības josla ir platāka un biezāka nekā parastajiem ienaidniekiem,
        # lai spēlētājs uzreiz saprastu, ka šis ir spēcīgāks pretinieks.
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            bar_width = 80
            bar_x = self.rect.centerx - (bar_width // 2)
            bar_y = self.rect.y - 15
            
            # Sarkanais fons (Zaudētā dzīvība)
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 6))
            # Zaļā priekšplāna josla (Atlikusī dzīvība)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, 6))