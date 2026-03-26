import pygame

class Player:
    def __init__(self):
        self.rect = pygame.Rect(400, 300, 40, 40)
        self.color = (0, 255, 0) # Green
        self.speed = 5
        self.money = 0

    def move(self, keys):
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)