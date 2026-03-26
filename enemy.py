import pygame

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 2

    def update(self, player_rect):
        # Basic tracking AI
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        if self.rect.y < player_rect.y: self.rect.y += self.speed
        if self.rect.y > player_rect.y: self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 50, 50), self.rect)