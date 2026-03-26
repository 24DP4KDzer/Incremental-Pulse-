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
        self.damage = 1.0  # <--- INITIALIZED HERE TO PREVENT CRASHES
        self.projectiles_count = 1
        self.base_cooldown = 25
        self.max_energy = 10.0  # Seconds
        self.energy = 10.0      # Current Seconds

        self.dash_unlocked = False
        self.dash_cooldown = 0
        self.magnet_range = 60 # Base pickup range
        self.skill_points = 0

        
        # Combat Stats
        self.char_type = "none"
        self.attack_style = "none"
        self.attacking = False
        self.attack_timer = 0
        self.attack_radius = 100
        self.attack_cooldown = 0

    def setup_class(self, char_type):
        self.char_type = char_type
        # We keep the base damage at 1.0, but you could vary it by class here!
        self.damage = 1.0 
        
        if char_type == "wizard":
            self.speed, self.max_health, self.color = 5, 80, (100, 200, 255)
            self.attack_radius, self.attack_style = 200, "homing"
        elif char_type == "shadow":
            self.speed, self.max_health, self.color = 8, 60, (150, 100, 255)
            self.attack_radius, self.attack_style = 150, "homing"
        elif char_type == "dwarf":
            self.speed, self.max_health, self.color = 3, 150, (255, 100, 100)
            self.attack_radius, self.attack_style = 120, "melee"
            self.damage = 1.5 # Dwarf hits a bit harder base
            
        self.health = self.max_health

    def move(self, keys):
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed

    def draw(self, screen):
        # Draw the main character body
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Visual for Melee Sweep (Dwarf)
        if self.attacking and self.attack_style == "melee":
            # Shrinking circle effect based on attack_timer
            alpha_radius = int(self.attack_radius * (self.attack_timer / 15))
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, alpha_radius, 3)
            
        # Visual for Homing Range (Wizard/Shadow)
        # This draws a very faint circle so you know how far you can shoot
        if self.attack_style == "homing":
            # Only draw a faint outline
            pygame.draw.circle(screen, self.color, self.rect.center, self.attack_radius, 1)