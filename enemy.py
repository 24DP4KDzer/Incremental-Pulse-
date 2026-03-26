import pygame

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.max_health = 5  # Give them a bit more life
        self.health = self.max_health
        self.speed = 2

    def update(self, player_rect):
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        if self.rect.y < player_rect.y: self.rect.y += self.speed
        if self.rect.y > player_rect.y: self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 50, 50), self.rect)
        # Health Bar logic
        bar_w = 40
        hp_ratio = max(0, self.health / self.max_health) # Prevents negative bars
        pygame.draw.rect(screen, (100, 0, 0), (self.rect.x, self.rect.y - 12, bar_w, 6))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 12, bar_w * hp_ratio, 6))