import pygame
import math

# Helper function to load images with a fallback
def load_sprite(path, size=(60, 60)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255)) 
        return surf

class Player:
    def __init__(self):
        # 1. SETUP RECT AND BASE ASSETS
        self.rect = pygame.Rect(100, 100, 100, 100)
        self.color = (0, 255, 0)
        
        self.img_left = load_sprite("photos/wizard_left.png", (100, 100))
        self.img_right = load_sprite("photos/pixil-frame-going-right.png", (100, 100))
        self.img_up = load_sprite("photos/pixil-frame-going-up.png", (100, 100))
        self.image = self.img_right

        self.shadow_surf = pygame.Surface((self.rect.width, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_surf, (0, 0, 0, 80), [0, 0, self.rect.width, 20])


        # --- DARKNESS SYSTEM SETUP ---
        # Get screen info for surface sizing
        display_info = pygame.display.Info()
        sw, sh = display_info.current_w, display_info.current_h
        
        self.darkness_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        self.darkness_intensity = 235  # Higher = darker map (0-255)
        
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
        
        self.dash_unlocked = True
        self.dash_cooldown = 0
        self.magnet_range = 60 
        self.skill_points = 0
        self.highscore = 1

        self.thorns = 0
        self.regen = 0.0
        self.gold_modifier = 1.0
        self.crit_chance = 0
        self.lifesteal = 0
        self.time_dilation = 1.0

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
        if keys[pygame.K_w]: 
            self.rect.y -= self.speed
            self.image = self.img_up
        if keys[pygame.K_s]: 
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.image = self.img_left
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.image = self.img_right

    def draw_darkness(self, screen, flicker_val):
        self.darkness_surf.fill((5, 5, 15, self.darkness_intensity))
        
        # 2. Calculate the "Light Hole" size
        pulse = int(6 * math.sin(flicker_val))
        # Making the light slightly larger than attack radius so you can see enemies coming
        light_radius = int(self.attack_radius * 1.4) + pulse
        
        # 3. Create the mask surface for the hole
        t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        
        # 4. Draw the smooth gradient (Step of 1 for perfect quality)
        # Inner core: perfectly clear
        pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), light_radius // 2)
        
        # Outer ring: fading out
        for r in range(light_radius, light_radius // 2, -1):
            # Calculate alpha to subtract from the shroud
            alpha_to_remove = int(255 * (1 - (r - light_radius // 2) / (light_radius // 2)))
            pygame.draw.circle(t_surf, (0, 0, 0, alpha_to_remove), (light_radius, light_radius), r)
        
        # 5. Subtract the light from the darkness shroud
        self.darkness_surf.blit(t_surf, t_surf.get_rect(center=self.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        
        # 6. Blit the finished shroud to the main screen
        screen.blit(self.darkness_surf, (0, 0))

    def draw(self, screen):
        # Increase the '+ 10' if it needs to go even further right
        shadow_pos = (self.rect.x + 25, self.rect.bottom + 45) 
        screen.blit(self.shadow_surf, shadow_pos)

        if self.dash_cooldown > 0:
            self.image.set_alpha(150) 
        else:
            self.image.set_alpha(255)

        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        if self.attacking and self.attack_style == "melee":
            alpha_radius = int(self.attack_radius * (self.attack_timer / 15))
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, alpha_radius, 3)