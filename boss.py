import pygame
import random

class Boss:
    def __init__(self, screen_w, screen_h):
        self.width, self.height = 250, 250
        self.rect = pygame.Rect(random.randint(0, screen_w-250), random.randint(0, screen_h-250), self.width, self.height)
        self.max_health = 150 # Absolute Tank
        self.health = self.max_health
        self.speed = 1.0 

    def update(self, player_rect):
        if self.rect.centerx < player_rect.centerx: self.rect.x += self.speed
        if self.rect.centerx > player_rect.centerx: self.rect.x -= self.speed
        if self.rect.centery < player_rect.centery: self.rect.y += self.speed
        if self.rect.centery > player_rect.centery: self.rect.y -= self.speed

    def draw(self, screen):
        # Boss Body
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=20)
        # Thick Health Bar
        hp_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (50, 0, 0), (self.rect.x, self.rect.y - 30, self.width, 15))
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 30, self.width * hp_ratio, 15))