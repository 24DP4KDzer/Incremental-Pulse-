import pygame
import random
import math

class Boss:
    def __init__(self, screen_w, screen_h):
        self.width, self.height = 250, 250
        self.rect = pygame.Rect(random.randint(0, screen_w-250), random.randint(0, screen_h-250), self.width, self.height)
        self.max_health = 150 # veri big hp
        self.health = self.max_health
        self.speed = 1.0 

    def update(self, player_rect, dilation=1.0):
        # Calculate direction to player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            #boss Slower
            self.rect.x += (dx / dist) * self.speed * dilation
            self.rect.y += (dy / dist) * self.speed * dilation

    def draw(self, screen):
        # Boss Body
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=20)
        # Thick Health Bar
        hp_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (50, 0, 0), (self.rect.x, self.rect.y - 30, self.width, 15))
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 30, self.width * hp_ratio, 15))