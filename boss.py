import pygame
import random

class Boss:
    def __init__(self, screen_w, screen_h):
        self.rect = pygame.Rect(random.randint(0, screen_w), random.randint(0, screen_h), 120, 120)
        self.health = 50
        self.max_health = 50
        self.speed = 1.5
        self.color = (255, 255, 255) # White/Boss Color

    def update(self, player_rect):
        # Slower but constant tracking
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        if self.rect.y < player_rect.y: self.rect.y += self.speed
        if self.rect.y > player_rect.y: self.rect.y -= self.speed

    def draw(self, screen):
        # Draw Boss Body
        pygame.draw.rect(screen, self.color, self.rect)
        # Health Bar above Boss
        hp_bar_width = self.rect.width
        hp_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (200, 0, 0), (self.rect.x, self.rect.y - 20, hp_bar_width, 10))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 20, hp_bar_width * hp_ratio, 10))