import pygame
import random

class Coin:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(50, 750), random.randint(50, 550), 20, 20)
        self.color = (255, 215, 0) # Gold

    def respawn(self):
        self.rect.x = random.randint(50, 750)
        self.rect.y = random.randint(50, 550)

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)