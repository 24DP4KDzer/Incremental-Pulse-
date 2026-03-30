import pygame
import math


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.max_health = 5 
        self.health = self.max_health
        self.speed = 2

    def update(self, player_rect, dilation=1.0):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            self.rect.x += (dx / dist) * self.speed * dilation
            self.rect.y += (dy / dist) * self.speed * dilation

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 50, 50), self.rect)
        bar_w = 40
        hp_ratio = max(0, self.health / self.max_health) # Prevents negative bars
        pygame.draw.rect(screen, (100, 0, 0), (self.rect.x, self.rect.y - 12, bar_w, 6))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 12, bar_w * hp_ratio, 6))