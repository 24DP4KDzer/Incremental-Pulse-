import pygame
import random

class Coin:
    # funkcija __init__ pieņem Coin tipa vērtību self un atgriež None tipa vērtību None
    def __init__(self):
        # [SAREŽĢĪTA LOĢIKA]: Attēla ielāde ar rezerves variantu (Fallback)
        # Mēģina ielādēt .png attēlu. Ja fails neeksistē vai ir norādīts nepareizs ceļš,
        # programma neapstājas (neizmet kļūdu), bet gan izpilda 'except' bloku un
        # uzzīmē vienkāršu krāsainu apli, lai spēle varētu turpināt darboties.
        try:
            self.image = pygame.image.load("photos/YellowCoin.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except:
            # Fallback if image is missing
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 150, 255), (10, 10), 10)
            
        self.rect = self.image.get_rect()

    # funkcija draw pieņem Coin tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class SpecialCoin:
    # funkcija __init__ pieņem SpecialCoin tipa vērtību self un atgriež None tipa vērtību None
    def __init__(self):
        try:
            self.image = pygame.image.load("photos/blueCoin.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (25, 25))
        except:
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 12)
            
        self.rect = self.image.get_rect()

    # funkcija draw pieņem SpecialCoin tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class HpCoin(Coin):
    # funkcija draw pieņem HpCoin tipa vērtību self un pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 128, 0), self.rect.center, (20))
    
    # funkcija respawn pieņem HpCoin tipa vērtību self, int tipa vērtību screen_w un int tipa vērtību screen_h un atgriež None tipa vērtību None
    def respawn(self, screen_w, screen_h):
        self.rect.center = (random.randint(50, screen_w-50), random.randint(50, screen_h-50))