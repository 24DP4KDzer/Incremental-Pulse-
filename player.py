import pygame

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 50, 50)
        self.color = (0, 255, 0)
        self.money = 0
        self.speed_level = 0
        self.range_level = 0
        
        # Base Stats
        self.speed = 1.3
        self.max_health = 100
        self.health = 100
        
        # Combat Stats
        self.char_type = "none"
        self.attack_style = "none"
        self.attacking = False
        self.attack_timer = 0
        self.attack_radius = 100
        self.attack_cooldown = 0

    def setup_class(self, char_type):
        self.char_type = char_type
        if char_type == "wizard":
            self.speed, self.max_health, self.color = 5, 80, (100, 200, 255)
            self.attack_radius, self.attack_style = 200, "homing"
        elif char_type == "shadow":
            self.speed, self.max_health, self.color = 8, 60, (150, 100, 255)
            self.attack_radius, self.attack_style = 150, "homing"
        elif char_type == "dwarf":
            self.speed, self.max_health, self.color = 3, 150, (255, 100, 100)
            self.attack_radius, self.attack_style = 120, "melee"
        self.health = self.max_health

    def move(self, keys):
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Visual for Melee Sweep
        if self.attacking and self.attack_style == "melee":
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.attack_radius, 3)