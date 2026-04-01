import pygame
import math

# --- HELPER FUNCTION FOR SPRITE SHEETS ---
def get_image_from_sheet(sheet, column, row, width, height, start_x=0, start_y=0, padding_x=0, padding_y=0, scale_size=(100, 100)):
    """Extracts a frame, accounting for starting positions and space between frames."""
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    
    exact_x = start_x + (column * width) + (column * padding_x)
    exact_y = start_y + (row * height) + (row * padding_y)
    
    crop_rect = pygame.Rect(exact_x, exact_y, width, height)
    image.blit(sheet, (0, 0), crop_rect)
    
    return pygame.transform.scale(image, scale_size)

class Player:
    def __init__(self):
        # 1. SETUP RECT AND BASE ASSETS
        self.rect = pygame.Rect(100, 100, 60, 80) # Hitbox size
        self.color = (0, 255, 0)
        
        # --- ANIMATION VARIABLES ---
        self.animations = {"up": [], "down": [], "left": [], "right": []}
        self.direction = "down"   
        self.frame_index = 0      
        self.anim_timer = 0       
        self.anim_speed = 0.15    
        self.image = None

        # Shadow under the player
        self.shadow_surf = pygame.Surface((self.rect.width, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_surf, (0, 0, 0, 80), [0, 0, self.rect.width, 20])

        # --- DARKNESS SYSTEM SETUP ---
        display_info = pygame.display.Info()
        sw, sh = display_info.current_w, display_info.current_h
        
        self.darkness_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        self.darkness_intensity = 235  
        
        # 2. PERMANENT STATS
        self.money = 0
        self.skill_points = 0
        self.highscore = 1
        
        # 3. ATTRIBUTES
        self.speed = 1.3
        self.max_health = 100
        self.health = 100
        self.damage = 1.0 
        self.projectile_count = 1
        self.base_cooldown = 25
        self.max_energy = 10.0
        self.energy = 10.0
        
        self.dash_unlocked = False
        self.dash_cooldown = 0
        self.magnet_range = 60 

        self.thorns = 0
        self.regen = 0.0
        self.armor = 0
        self.gold_modifier = 1.0
        self.crit_chance = 0
        self.lifesteal = 0

        # 4. COMBAT STATE
        self.char_type = "none"
        self.attack_style = "none"
        self.attacking = False
        self.attack_timer = 0
        self.attack_radius = 100
        self.attack_cooldown = 0

    def setup_class(self, char_type):
        """Sets unique stats and slices the correct sprite sheet."""
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
            
        # 1. LOAD THE SPRITE SHEET
        try:
            if char_type == "shadow":
                sheet = pygame.image.load("photos/allOfShadow.png").convert_alpha()
            else:
                sheet = pygame.image.load(f"photos/{char_type}_sheet.png").convert_alpha()
        except:
            sheet = pygame.Surface((200, 200), pygame.SRCALPHA)
            sheet.fill((255, 0, 255))

        # 2. CLEAR PREVIOUS ANIMATIONS
        self.animations = {"up": [], "down": [], "left": [], "right": []}

        # 3. SET SLICE DIMENSIONS (Adjust these to fit your image perfectly)
        frame_w = 100     # Width of the box
        frame_h = 143       # Height of the box
        start_x = 258      # Distance from left edge to the first box
        start_y = 252     # Distance from top edge to the first box
        padding_x = 47     # Empty space between columns
        padding_y = 55     # Empty space between rows
        num_frames = 2     # 4 frames per animation
        
        # 4. SLICE THE SHEET INTO LISTS
        for i in range(num_frames):
            # Normal UP and DOWN (Row 0 and Row 1)
            self.animations["up"].append(get_image_from_sheet(sheet, i, 0, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
            self.animations["down"].append(get_image_from_sheet(sheet, i, 1, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
            
            # Grab the RIGHT facing image (Row 3)
            img_right = get_image_from_sheet(sheet, i, 3, frame_w, frame_h, start_x, start_y, padding_x, padding_y)
            self.animations["right"].append(img_right)
            
            # Flip the RIGHT image horizontally to make it face LEFT!
            # pygame.transform.flip(image, flip_x, flip_y)
            img_left = pygame.transform.flip(img_right, True, False)
            self.animations["left"].append(img_left)

        # Set initial image
        self.direction = "down"
        self.frame_index = 0
        self.image = self.animations["down"][0]
        self.health = self.max_health

    def move(self, keys):
        is_moving = False
        
        # Check Up and Down
        if keys[pygame.K_w]: 
            self.rect.y -= self.speed
            self.direction = "up"
            is_moving = True
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.direction = "down"
            is_moving = True
            
        # Check Left and Right (Using 'if' instead of 'elif'!)
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
            is_moving = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
            is_moving = True

        # Handle animation logic
        if is_moving:
            self.anim_timer += self.anim_speed
            if self.anim_timer >= len(self.animations[self.direction]):
                self.anim_timer = 0
            self.frame_index = int(self.anim_timer)
        else:
            self.frame_index = 0 
            self.anim_timer = 0
            
        # Update the current image!
        if len(self.animations[self.direction]) > 0:
            self.image = self.animations[self.direction][self.frame_index]

    def draw_darkness(self, screen, flicker_val):
        """Renders the darkness shroud and the light circle around the player."""
        self.darkness_surf.fill((5, 5, 15, self.darkness_intensity))
        pulse = int(6 * math.sin(flicker_val))
        light_radius = int(self.attack_radius * 1.4) + pulse
        t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), light_radius // 2)
        for r in range(light_radius, light_radius // 2, -1):
            alpha_to_remove = int(255 * (1 - (r - light_radius // 2) / (light_radius // 2)))
            pygame.draw.circle(t_surf, (0, 0, 0, alpha_to_remove), (light_radius, light_radius), r)
        self.darkness_surf.blit(t_surf, t_surf.get_rect(center=self.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(self.darkness_surf, (0, 0))

    def draw(self, screen):
        """Draws shadow and player sprite with transparency effects."""
        # Draw Shadow
        shadow_pos = (self.rect.x, self.rect.bottom - 10) 
        screen.blit(self.shadow_surf, shadow_pos)

        # SAFELY Draw Player Sprite
        if self.image:
            # Handle Dash transparency
            if self.dash_cooldown > 0:
                self.image.set_alpha(150) 
            else:
                self.image.set_alpha(255)

            draw_pos = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, draw_pos)
        else:
            # Fallback if image fails to load completely
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Visual effect for Melee attacks
        if self.attacking and self.attack_style == "melee":
            alpha_radius = int(self.attack_radius * (self.attack_timer / 15))
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, alpha_radius, 3)