import pygame
import random

class Coin:
    def __init__(self):
        # Load and scale the image
        try:
            self.image = pygame.image.load("photos/YellowCoin.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except:
            # Fallback if image is missing
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 150, 255), (10, 10), 10)
            
        self.rect = self.image.get_rect()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class SpecialCoin:
    def __init__(self):
        try:
            self.image = pygame.image.load("photos/blueCoin.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (25, 25))
        except:
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 12)
            
        self.rect = self.image.get_rect()

    def draw(self, surface):
        surface.blit(self.image, self.rect)



class HpCoin(Coin):
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 128, 0), self.rect.center, (20))
    
    def respawn(self, screen_w, screen_h):
        self.rect.center = (random.randint(50, screen_w-50), random.randint(50, screen_h-50))