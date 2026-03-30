import pygame

# Helper function to load images with a fallback
def load_sprite(path, size=(60, 60)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        # If image fails to load, create a colored square so the game doesn't crash
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255)) # Pink is the universal "missing texture" color
        return surf

class Player:
    def __init__(self):
        # 1. SETUP RECT AND BASE ASSETS
        self.rect = pygame.Rect(100, 100, 60, 60)
        self.color = (0, 255, 0)
        
        # Pre-load images to memory for smooth movement
        self.img_left = load_sprite("photos/wizard_left.png")
        self.img_right = load_sprite("photos/pixil-frame-going-right.png")
        self.img_up = load_sprite("photos/pixil-frame-going-up.png")
        
        # Default starting image
        self.image = self.img_right 
        
        # 2. STATS
        self.money = 0
        self.speed_level = 0
        self.range_level = 0
        self.speed = 1.3
        self.max_health = 100
        self.health = 100
        self.damage = 1.0 
        self.projectiles_count = 1
        self.base_cooldown = 25
        self.max_energy = 10.0
        self.energy = 10.0
        
        self.dash_unlocked = False
        self.dash_cooldown = 0
        self.magnet_range = 60 
        self.skill_points = 0
        self.highscore = 1

        # 3. COMBAT STATS
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
            self.damage = 1.5 
            
        self.health = self.max_health

    def move(self, keys):
        # Handle Movement and Sprite Swapping simultaneously
        if keys[pygame.K_w]: 
            self.rect.y -= self.speed
            self.image = self.img_up
            
        if keys[pygame.K_s]: 
            self.rect.y += self.speed
            # (Optional: Add a down-facing sprite here if you make one)
            
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.image = self.img_left
            
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.image = self.img_right

    def draw(self, screen):
        # Draw the Sprite Image instead of just a rectangle
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Visual for Melee Sweep (Dwarf)
        if self.attacking and self.attack_style == "melee":
            alpha_radius = int(self.attack_radius * (self.attack_timer / 15))
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, alpha_radius, 3)
            
        # Visual for Homing Range Outline
        if self.attack_style == "homing":
            pygame.draw.circle(screen, self.color, self.rect.center, self.attack_radius, 1)