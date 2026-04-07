import pygame
import random

class Coin:
    _cached_image = None

    # funkcija __init__ pieņem Coin tipa vērtību self un atgriež None tipa vērtību None
    def __init__(self):
        # [SAREŽĢĪTA LOĢIKA]: Attēla ielāde ar rezerves variantu (Fallback)
        if self.__class__._cached_image is None:
            try:
                image = pygame.image.load("photos/YellowCoin.png").convert_alpha()
                image = pygame.transform.scale(image, (20, 20))
            except:
                image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(image, (0, 150, 255), (10, 10), 10)
            self.__class__._cached_image = image

        self.image = self.__class__._cached_image
        self.rect = self.image.get_rect()

    # funkcija draw pieņem Coin tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class SpecialCoin:
    _cached_image = None

    # funkcija __init__ pieņem SpecialCoin tipa vērtību self un atgriež None tipa vērtību None
    def __init__(self):
        if self.__class__._cached_image is None:
            try:
                image = pygame.image.load("photos/blueCoin.png").convert_alpha()
                image = pygame.transform.scale(image, (25, 25))
            except:
                image = pygame.Surface((25, 25), pygame.SRCALPHA)
                pygame.draw.circle(image, (255, 215, 0), (12, 12), 12)
            self.__class__._cached_image = image

        self.image = self.__class__._cached_image
        self.rect = self.image.get_rect()

    # funkcija draw pieņem SpecialCoin tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class HpCoin:
    _cached_image = None

    def __init__(self, x, y):
        self.posx = float(x)
        self.posy = float(y)
        self.rect = pygame.Rect(x, y, 30, 30) # Monētas izmērs
        
        if self.__class__._cached_image is None:
            try:
                image = pygame.image.load("photos/hp_coin.png").convert_alpha()
                image = pygame.transform.scale(image, (30, 30))
            except:
                image = pygame.Surface((30, 30), pygame.SRCALPHA)
                image.fill((255, 0, 0))
            self.__class__._cached_image = image

        self.image = self.__class__._cached_image

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Chest:
    _cached_image = None

    # funkcija __init__ pieņem Chest tipa vērtību self, int tipa vērtību x un int tipa vērtību y un atgriež None tipa vērtību None
    def __init__(self, x, y):
        if self.__class__._cached_image is None:
            try:
                image = pygame.image.load("photos/chest.png").convert_alpha()
                image = pygame.transform.scale(image, (90, 90))
            except:
                image = pygame.Surface((40, 40), pygame.SRCALPHA)
                image.fill((255, 215, 0))
            self.__class__._cached_image = image

        self.image = self.__class__._cached_image
        self.rect = self.image.get_rect(topleft=(x, y))

    # funkcija draw pieņem Chest tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        surface.blit(self.image, self.rect)
