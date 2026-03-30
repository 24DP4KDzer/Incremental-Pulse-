import pygame
import random

class Coin:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 20, 20)
    
    def respawn(self, screen_w, screen_h):
        self.rect.center = (random.randint(50, screen_w-50), random.randint(50, screen_h-50))
        
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 215, 0), self.rect.center, 10)


class SpecialCoin(Coin):
    def respawn(self, screen_w, screen_h):
        self.rect.center = (random.randint(50, screen_w-50), random.randint(50, screen_h-50))
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 255, 255), self.rect.center, 15)



class HpCoin(Coin):
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 128, 0), self.rect.center, (20))
    
    def respawn(self, screen_w, screen_h):
        self.rect.center = (random.randint(50, screen_w-50), random.randint(50, screen_h-50))