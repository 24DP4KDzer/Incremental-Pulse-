import pygame

class Projectile:
    def __init__(self, x, y, target, color, max_range):
        self.start_pos = pygame.math.Vector2(x, y)
        self.pos = pygame.math.Vector2(x, y)
        self.target = target
        self.speed = 10
        self.radius = 8
        self.color = color
        self.max_range = max_range # Range limit
        self.rect = pygame.Rect(x, y, self.radius*2, self.radius*2)

    def update(self, enemies_list):
        # 1. Range Check: Destroy if it goes too far
        if self.pos.distance_to(self.start_pos) > self.max_range:
            return False

        # 2. Homing Logic
        if self.target in enemies_list:
            direction = pygame.math.Vector2(self.target.rect.center) - self.pos
            if direction.length() > 0:
                direction.normalize_ip()
            self.pos += direction * self.speed
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            return True 
        return False 

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius)